"""
Study Planning Agent

Run:
    python study_planner.py

This demo keeps the architecture small but explicit:
- Notes Finder Subagent: searches course_notes.txt
- Conditional Context Chain: uses matching notes or model-generated material
- Cheatsheet and Study Plan Subagents: run in parallel from the same notes
- Save Tool: writes the latest cheatsheet and plan to study_plan.txt
- Memory: chat_history lets follow-ups revise the previous output
"""

import re
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import (
    RunnableBranch,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


# These paths stay relative to this file, so the script works from any folder.
PROJECT_DIR = Path(__file__).resolve().parent
NOTES_FILE = PROJECT_DIR / "course_notes.txt"
OUTPUT_FILE = PROJECT_DIR / "study_plan.txt"

# Load OPENAI_API_KEY from lodge_project/.env, matching the README setup.
load_dotenv(PROJECT_DIR / ".env")

# One model is reused by the main agent and the two LCEL subagent chains.
model = ChatOpenAI(model="gpt-4o-mini")

# This chain supplies study material only when course_notes.txt has no match.
fallback_notes_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You create accurate, beginner-friendly study material for a student.",
        ),
        (
            "human",
            """The local course notes do not cover this topic: {topic}

Create concise source material for the next study workflow. Explain key ideas,
plain definitions, important rules or formulas, and a simple example if useful.
Do not claim this material came from the course notes.""",
        ),
    ]
)
fallback_notes_chain = fallback_notes_prompt | model | StrOutputParser()

# The Cheatsheet Subagent turns note context into memory-friendly study notes.
cheatsheet_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You create concise student cheatsheets grounded only in provided notes.",
        ),
        (
            "human",
            """Topic: {topic}

Notes:
{notes}

Create one cheatsheet with:
- key ideas
- definitions
- formulas or rules if useful
- memory cues

If the notes do not contain enough information, say what is missing.""",
        ),
    ]
)
cheatsheet_chain = cheatsheet_prompt | model | StrOutputParser()

# The Study Plan Subagent uses the same notes as the cheatsheet subagent, so
# both chains can start at the same time after the notes have been found.
study_plan_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You create practical study plans with content tasks and practice tasks.",
        ),
        (
            "human",
            """Topic: {topic}
Number of study sessions: {sessions}
Subtopic needing more practice: {practice_focus}

Notes:
{notes}

Break the topic into subtopics, then create a study plan.
For each session, include:
- Content: information and notes to understand or commit to memory
- Practice: skills and common problem types the student must solve

Default to one session when the user does not specify a session count. If a
practice focus is provided, add more practice tasks for that subtopic.""",
        ),
    ]
)
study_plan_chain = study_plan_prompt | model | StrOutputParser()

# RunnableParallel sends one shared input dictionary to both independent
# subagents. It returns {"cheatsheet": ..., "study_plan": ...} when both finish.
parallel_study_output_chain = RunnableParallel(
    cheatsheet=cheatsheet_chain,
    study_plan=study_plan_chain,
)


def _words(text: str) -> set[str]:
    """Normalize text into lowercase words for simple keyword search."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _read_notes() -> list[str]:
    """Read non-empty note lines from course_notes.txt."""
    if not NOTES_FILE.exists():
        return []
    return [line.strip() for line in NOTES_FILE.read_text().splitlines() if line.strip()]


def _matching_note_lines(query: str, notes: list[str]) -> list[str]:
    """Return the strongest note lines with at least one keyword match."""
    query_words = _words(query)
    scored = [
        (len(query_words & _words(note)), note)
        for note in notes
        if query_words & _words(note)
    ]
    return [note for _, note in sorted(scored, reverse=True)[:8]]


def _format_notes(notes: list[str]) -> str:
    """Format note lines consistently for tools and prompt context."""
    return "\n".join(f"- {note}" for note in notes)


# The condition is computed once, then RunnableBranch chooses the local-note or
# model fallback context before the two downstream subagents run in parallel.
context_with_matches = RunnablePassthrough.assign(
    matching_notes=lambda inputs: _matching_note_lines(
        inputs["topic"], _read_notes()
    )
)
conditional_context_chain = context_with_matches | RunnableBranch(
    (
        lambda inputs: bool(inputs["matching_notes"]),
        RunnablePassthrough.assign(
            notes=lambda inputs: _format_notes(inputs["matching_notes"]),
            source=lambda _: "course_notes.txt",
        ),
    ),
    RunnablePassthrough.assign(
        notes=fallback_notes_chain,
        source=lambda _: (
            "Model-generated study material because course_notes.txt had "
            "no relevant match."
        ),
    ),
)

# Tools the final orchestrator agent can call.

@tool
def search_notes(query: str) -> str:
    """
    Find note lines that match the requested study topic.

    Use this first whenever the user asks to study a topic or revise a plan for
    a subtopic.
    """
    query_words = _words(query)
    notes = _read_notes()

    if not notes:
        return "No notes found. Add study notes to course_notes.txt."
    if not query_words:
        return "\n".join(notes[:8])

    matching_notes = _matching_note_lines(query, notes)
    if not matching_notes:
        return "No exact note matches found. Closest available notes:\n" + "\n".join(
            f"- {note}" for note in notes[:8]
        )

    return _format_notes(matching_notes)


@tool
def create_cheatsheet(topic: str, notes: str) -> str:
    """
    Run the Cheatsheet Subagent chain.

    Use this after search_notes so the cheatsheet is grounded in course_notes.txt.
    """
    return cheatsheet_chain.invoke({"topic": topic, "notes": notes})


@tool
def create_study_plan(
    topic: str,
    notes: str,
    sessions: int = 1,
    practice_focus: str = "none",
) -> str:
    """
    Run the Study Plan Subagent chain by itself.

    This teaching tool accepts searched notes directly. The normal workflow
    uses create_and_save_study_output to run this chain alongside the
    cheatsheet chain.
    """
    return study_plan_chain.invoke(
        {
            "topic": topic,
            "notes": notes,
            "sessions": sessions or 1,
            "practice_focus": practice_focus or "none",
        }
    )


@tool
def save_study_output(
    topic: str,
    cheatsheet: str,
    study_plan: str,
    source: str = "course_notes.txt",
) -> str:
    """
    Save the latest cheatsheet and study plan, including their source label.

    Use this every time a new or revised study plan is created.
    """
    OUTPUT_FILE.write_text(
        f"# Source\n\n{source}\n\n# {topic} Cheatsheet\n\n{cheatsheet}\n\n"
        f"# Study Plan\n\n{study_plan}\n"
    )
    return f"Saved cheatsheet and study plan to {OUTPUT_FILE.name}. Source: {source}"


@tool
def create_and_save_study_output(
    topic: str,
    sessions: int = 1,
    practice_focus: str = "none",
) -> str:
    """
    Create and save a complete cheatsheet and study plan for a topic.

    This is the normal workflow tool. It uses matching course notes when
    available, otherwise creates model-generated study material, then sends the
    selected context to both subagents in parallel and saves their paired output.
    """
    context = conditional_context_chain.invoke(
        {
            "topic": topic,
            "sessions": sessions or 1,
            "practice_focus": practice_focus or "none",
        }
    )
    output = parallel_study_output_chain.invoke(context)
    saved_message = save_study_output.invoke(
        {
            "topic": topic,
            "cheatsheet": output["cheatsheet"],
            "study_plan": output["study_plan"],
            "source": context["source"],
        }
    )
    return (
        f"{saved_message}\n\n# Source\n\n{context['source']}\n\n"
        f"# {topic} Cheatsheet\n\n{output['cheatsheet']}\n\n"
        f"# Study Plan\n\n{output['study_plan']}"
    )


def build_agent() -> AgentExecutor:
    """Build the main Study Planning Agent that coordinates the subagents."""
    tools = [
        search_notes,
        create_cheatsheet,
        create_study_plan,
        save_study_output,
        create_and_save_study_output,
    ]

    # MessagesPlaceholder("chat_history") gives the agent short-term memory.
    agent_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a Study Planning Agent.

Your job:
1. Identify the study topic from the user.
2. Use create_and_save_study_output for every new or revised study request.
   It uses relevant course notes when available, otherwise creates model
   fallback material, runs the cheatsheet and study-plan subagents in parallel,
   and saves the result with a source label.
3. The individual tools are available only to explain or demonstrate each
   workflow step when the user explicitly asks about them.

Defaults:
- If the user does not specify study sessions, use 1 session.
- If the user asks for more sessions, revise the previous plan using chat history.
- If the user asks for more practice on a subtopic, revise the practice tasks for that subtopic.

Final answer format:
- Briefly state what was created or revised.
- Show the cheatsheet.
- Show the study plan.
- Mention that study_plan.txt was saved.""",
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    # create_tool_calling_agent lets the model choose which tools to call.
    agent = create_tool_calling_agent(model, tools, agent_prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


def main() -> None:
    """Run a terminal chat loop with in-memory conversation history."""
    agent_executor = build_agent()
    chat_history = []

    print("Study Planning Agent")
    print("Ask for a topic cheatsheet and study plan. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break

        # Send all previous messages so the agent can revise prior plans.
        result = agent_executor.invoke(
            {"input": user_input, "chat_history": chat_history}
        )
        answer = result["output"]

        # Store this turn after the model answers, matching the chat model demo.
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=answer))

        print(f"\nAgent: {answer}\n")


if __name__ == "__main__":
    main()
