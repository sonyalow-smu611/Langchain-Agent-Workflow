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

Create the environment file in this `study_langchain/` folder, where `study_resource_generator.py` loads it:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

`.env` is listed in `.gitignore`, so your key is not committed.

## Add Study Documents

The `documents/` folder ships with `photosynthesis.txt`, a short sample so the first run has something to work with. Add your own plain text files next to it, or replace it:

```bash
cp /path/to/your-notes.txt documents/
```

Only `.txt` files are loaded, read as UTF-8.

## Run

With the virtual environment active:

```bash
python study_resource_generator.py
```

The script will:

1. Load `.txt` files from `study_langchain/documents/`.
2. Split them into chunks.
3. Embed them with `text-embedding-3-small`.
4. Store them in an in-memory Chroma vector store that uses cosine distance.
5. Retrieve up to 4 chunks that score at least 0.2 for your topic.
6. Use `gpt-4o-mini` to generate the selected study resource.

If no chunk scores high enough, the script says no notes matched and skips the model call. Try a more specific topic, or add notes that cover it.

## Use

Choose one of the menu options:

```text
1. Cheatsheet
2. 1 page summary
3. In depth organised notes
4. Quiz
```

Then enter a topic, chapter, or question to focus retrieval and generation.

Type `exit` at the menu, or press Ctrl-D, to quit.

## Run As A Streamlit App

The same agent has a chat front end in `app.py`:

```bash
streamlit run app.py
```

Streamlit prints a local URL such as `http://localhost:8501`. Open it, pick a study resource in the sidebar, then type a topic in the chat box. Later requests see the earlier ones in chat history, like the CLI.

The vector store is cached while the app runs. After adding or editing files in `documents/`, click **Reload notes** in the sidebar. **Clear chat** starts a fresh conversation.

## Notes

The vector store is rebuilt every time you run the script. Add or edit files in `documents/`, then rerun the script to refresh the study context.

## Test

Run these from the `study_langchain/` folder:

```bash
pytest -m "not live"   # the whole CLI with a fake model, no API key needed
pytest -m live         # real OpenAI calls using the key in .env
```

`tests/test_app.py` drives the Streamlit app with Streamlit's `AppTest`, so these commands cover the CLI and the app.

Live tests are skipped when `OPENAI_API_KEY` is missing. They take about 30 seconds and cost well under a cent.
