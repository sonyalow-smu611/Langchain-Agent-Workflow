# Study Planning Agent

This is a small LangChain CLI agent that turns course notes into one topic cheatsheet and one study plan.

The default plan is for `1` study session. If the user asks for more sessions, the agent spreads the topic across those sessions. If the user asks for more practice on a subtopic, the agent revises the practice tasks for that subtopic.

## What It Does

- Reads notes from `course_notes.txt`.
- Searches for the topic the user wants to study.
- Creates one cheatsheet for that topic.
- Breaks the topic into subtopics.
- Creates study tasks split into:
  - `Content`: information and notes to understand or memorize.
  - `Practice`: skills and common problem types to solve.
- Saves the latest result to `study_plan.txt`.

## Agent Pieces

- `Notes Finder Subagent`: uses `search_notes()` to find relevant notes.
- `Cheatsheet Subagent`: uses `cheatsheet_prompt | model | StrOutputParser()`.
- `Study Plan Subagent`: uses `study_plan_prompt | model | StrOutputParser()`.
- `Parallel Workflow`: uses `RunnableParallel` to run both subagents from the same searched notes.
- `Combined Tool`: uses `create_and_save_study_output()` to search, generate, and save one complete result.
- `Save Tool`: uses `save_study_output()` to write the latest cheatsheet and plan.
- `Memory`: uses an in-memory `chat_history` list for follow-up revisions during the same run.

## Setup

Use Python `3.13` for this project. The LangChain `0.3.x` APIs used by this demo are not compatible with Python `3.14`.

From the repo root:

```bash
cd "lodge_project"
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Confirm that the active environment uses Python 3.13 before running the agent:

```bash
python --version
```

Edit `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Run In The Terminal

```bash
python study_planner.py
```

## Run As A Local Streamlit App

```bash
streamlit run app.py
```

Streamlit will print a local URL such as:

```text
http://localhost:8501
```

Open that URL in your browser and chat with the same Study Planning Agent from `study_planner.py`.

Example prompts:

```text
I want to study transformers and attention.
```

```text
Make it 3 study sessions.
```

```text
Give me more practice on tokens, embeddings, and self-attention.
```

Type `exit` to quit.
