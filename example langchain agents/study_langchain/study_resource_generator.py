"""
Interactive CLI: turns your own .txt notes into a cheatsheet, summary, in-depth
notes, or quiz — grounded only in documents you drop into documents/.

Run: add .txt files to study_langchain/documents/, then
     `python study_resource_generator.py` (needs OPENAI_API_KEY in the shared
     repo-root .env).

Learn: RAG (TextLoader -> CharacterTextSplitter -> Chroma -> similarity
       retriever), multiple prompt-templated LCEL chains sharing one
       retriever, routing user input to different chains, and manually
       formatting chat history into a prompt variable.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.schema.output_parser import StrOutputParser
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

current_dir = os.path.dirname(os.path.abspath(__file__))
documents_dir = os.path.join(current_dir, "documents")


def create_study_agents():
    """
    Build the four LCEL chains used by the CLI.

    Each chain shares the same chat model but has a different prompt, so the
    user can generate a cheatsheet, summary, organized notes, or quiz from the
    same retrieved study context.
    """
    model = ChatOpenAI(model="gpt-4o-mini")

    # A LangChain prompt template stores reusable instructions and variables.
    # The chain later fills in chat_history, context, and focus at runtime.

    # The cheatsheet agent creates short, high-signal revision notes.
    cheatsheet_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a study assistant that creates concise cheatsheets from provided study resources.",
            ),
            (
                "human",
                """Use only the study context below and the chat history to create a cheatsheet.

Chat history:
{chat_history}

Study context:
{context}

Focus:
{focus}

Create a cheatsheet with key definitions, formulas, dates, concepts, and quick memory cues. If the answer is not in the study context, say what is missing.""",
            ),
        ]
    )
    cheatsheet_chain = cheatsheet_template | model | StrOutputParser()


    # The summary agent compresses the topic into a one-page style overview.
    summary_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a study assistant that writes clear one-page summaries from provided study resources.",
            ),
            (
                "human",
                """Use only the study context below and the chat history to write a one-page summary.

Chat history:
{chat_history}

Study context:
{context}

Focus:
{focus}

Write a clear summary with the main idea, important details, and final takeaway. If the answer is not in the study context, say what is missing.""",
            ),
        ]
    )
    summary_chain = summary_template | model | StrOutputParser()


    # The notes agent expands the retrieved material into organized study notes.
    notes_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a study assistant that creates in-depth organized notes from provided study resources.",
            ),
            (
                "human",
                """Use only the study context below and the chat history to create organized notes.

Chat history:
{chat_history}

Study context:
{context}

Focus:
{focus}

Create in-depth notes with headings, bullet points, examples, and important relationships between ideas. If the answer is not in the study context, say what is missing.""",
            ),
        ]
    )
    notes_chain = notes_template | model | StrOutputParser()


    # The quiz agent turns the retrieved material into practice questions and answers.
    quiz_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a study assistant that creates quizzes from provided study resources.",
            ),
            (
                "human",
                """Use only the study context below and the chat history to create a quiz.

Chat history:
{chat_history}

Study context:
{context}

Focus:
{focus}

Create 10 mixed question types with an answer key at the end. If there is not enough information in the study context, create fewer questions and say what is missing.""",
            ),
        ]
    )
    quiz_chain = quiz_template | model | StrOutputParser()


    return {
        "cheatsheet": cheatsheet_chain,
        "summary": summary_chain,
        "notes": notes_chain,
        "quiz": quiz_chain,
    }


def load_study_documents():
    """
    Load all local .txt files that the RAG system should search over.

    The function creates the documents folder if it does not exist, reads each
    text file with TextLoader, and stores the file name in metadata so generated
    answers can show which source chunk they used.
    """
    os.makedirs(documents_dir, exist_ok=True)

    # Only plain text files are supported in this beginner example.
    text_files = [file for file in os.listdir(documents_dir) if file.endswith(".txt")]
    if not text_files:
        return []

    documents = []
    for text_file in text_files:
        file_path = os.path.join(documents_dir, text_file)
        loader = TextLoader(file_path)
        loaded_docs = loader.load()

        # Keep the original file name attached to each loaded document.
        for doc in loaded_docs:
            doc.metadata = {"source": text_file}
            documents.append(doc)

    return documents


def create_retriever(documents):
    """
    Turn loaded documents into a searchable retriever.

    Long documents are split into smaller chunks, converted into OpenAI
    embeddings, stored in Chroma, then exposed through a similarity retriever
    that returns the most relevant chunks for the user's focus question.
    """
    # Chunking keeps retrieved context small enough to fit into the model prompt.
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    # Embeddings convert text chunks into vectors that Chroma can compare.
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    db = Chroma.from_documents(docs, embeddings)

    # The threshold filters out weak matches instead of sending every result.
    return db.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 4, "score_threshold": 0.2},
    )


def route_choice(choice, study_agents):
    """
    Map a menu option or typed command to the matching study chain.

    Returns both the agent name and the chain so the caller can label output and
    invoke the selected prompt. Invalid choices return (None, None).
    """
    # Accept both numbered menu choices and simple text aliases.
    routes = {
        "1": "cheatsheet",
        "cheatsheet": "cheatsheet",
        "2": "summary",
        "summary": "summary",
        "3": "notes",
        "in depth organised notes": "notes",
        "in depth organized notes": "notes",
        "organized notes": "notes",
        "organised notes": "notes",
        "4": "quiz",
        "quiz": "quiz",
    }

    agent_name = routes.get(choice.lower().strip())
    if not agent_name:
        return None, None

    return agent_name, study_agents[agent_name]


def retrieve_context(retriever, focus):
    """
    Ask the retriever for study chunks related to the user's focus.

    The returned LangChain documents are formatted into plain text with their
    source names, because the prompt templates expect a single context string.
    """
    relevant_docs = retriever.invoke(focus)

    if not relevant_docs:
        return "No relevant study context was found."

    # Join chunks with spacing so the model can read them as separate sources.
    return "\n\n".join(
        [
            f"Source: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
            for doc in relevant_docs
        ]
    )


def format_chat_history(chat_history):
    """
    Convert LangChain chat message objects into readable prompt text.

    The prompt templates use a plain {chat_history} variable, so this function
    turns SystemMessage, HumanMessage, and AIMessage objects into labeled lines.
    """
    formatted_messages = []

    for message in chat_history:
        # Preserve the role label so the model can distinguish prior turns.
        if isinstance(message, SystemMessage):
            role = "System"
        elif isinstance(message, HumanMessage):
            role = "Human"
        elif isinstance(message, AIMessage):
            role = "AI"
        else:
            role = "Message"

        formatted_messages.append(f"{role}: {message.content}")

    return "\n".join(formatted_messages)


def print_menu():
    """
    Print the CLI menu for the user.

    Keeping this in one function makes the chat loop easier to read and keeps
    the display text in one place.
    """
    print("\nChoose a study resource to generate:")
    print("1. Cheatsheet")
    print("2. 1 page summary")
    print("3. In depth organised notes")
    print("4. Quiz")
    print("Type 'exit' to quit.")


def run_chat():
    """
    Run the full interactive RAG workflow.

    This loads study files, builds the retriever and chains, then repeatedly
    asks the user what to generate and what topic to focus on until they exit.
    """
    # Documents must exist before we spend time creating embeddings or chains.
    documents = load_study_documents()
    if not documents:
        print(f"No .txt study resources found in {documents_dir}.")
        print("Add your study resources to that folder and run this script again.")
        return

    # The retriever is built once per run and reused for every menu request.
    print("Loading study resources and creating vector store...")
    retriever = create_retriever(documents)
    study_agents = create_study_agents()

    # Chat history gives later generations some memory of earlier requests.
    chat_history = [
        SystemMessage(
            content="You are a helpful study assistant that only uses the uploaded study resources."
        )
    ]

    print("Study Resource Generator is ready.")

    while True:
        print_menu()
        choice = input("\nYour choice: ")

        if choice.lower().strip() == "exit":
            break

        agent_name, agent_chain = route_choice(choice, study_agents)
        if agent_chain is None:
            print(
                "Sorry, I did not understand that choice. "
                "Please choose 1, 2, 3, 4, or exit."
            )
            continue

        focus = input("Enter the topic, chapter, or question to focus on: ")
        if not focus.strip():
            print("Please enter a topic, chapter, or question.")
            continue

        # Store the user's request before invoking the selected chain.
        human_message = f"Generate {agent_name} for: {focus}"
        chat_history.append(HumanMessage(content=human_message))

        # Retrieve relevant chunks, then pass them into the chosen prompt chain.
        context = retrieve_context(retriever, focus)
        response = agent_chain.invoke(
            {
                "chat_history": format_chat_history(chat_history),
                "context": context,
                "focus": focus,
            }
        )

        # Save and display the answer so future turns can refer to it.
        chat_history.append(AIMessage(content=response))
        print(f"\n--- {agent_name.title()} ---")
        print(response)

    print("\n---- Message History ----")
    print(chat_history)


if __name__ == "__main__":
    run_chat()
