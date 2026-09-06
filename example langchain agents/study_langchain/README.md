# Study Resource Generator

Interactive LangChain RAG CLI that turns local `.txt` study documents into a cheatsheet, one-page summary, organized notes, or a quiz.

## Setup

From the repo root:

```bash
cd "example langchain agents/study_langchain"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create the environment file where `study_resource_generator.py` loads it:

```bash
cp .env.example ../.env
```

Edit `../.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Add Study Documents

Put one or more plain text files in the local `documents/` folder:

```bash
mkdir -p documents
cp /path/to/your-notes.txt documents/
```

** Only `.txt` files are loaded by `load_study_documents()`. **

## Run

With the virtual environment active:

```bash
python study_resource_generator.py
```

The script will:

1. Load `.txt` files from `study_langchain/documents/`.
2. Split them into chunks.
3. Embed them with `text-embedding-3-small`.
4. Store them in an in-memory Chroma vector store.
5. Use `gpt-4o-mini` to generate the selected study resource.

## Use

Choose one of the menu options:

```text
1. Cheatsheet
2. 1 page summary
3. In depth organised notes
4. Quiz
```

Then enter a topic, chapter, or question to focus retrieval and generation.

Type `exit` at the menu to quit.

## Notes

The vector store is rebuilt every time you run the script. Add or edit files in `documents/`, then rerun the script to refresh the study context.
