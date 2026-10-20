# Make the Study Resource Generator run and produce study resources

Status: ready-for-agent

## Problem Statement

A learner following the study_langchain README installs the requirements, starts the Study Resource Generator, and gets a crash before the menu appears: `ModuleNotFoundError: No module named 'langchain.prompts'`. The script was written for LangChain 0.x. The README installs unpinned packages, so learners get LangChain 1.x, which removed `langchain.prompts`, `langchain.schema`, `langchain.schema.output_parser` and `langchain.text_splitter`.

Fixing the imports is not enough on its own to produce a study resource:

- The project ships no `documents/` folder and no sample study document. A fresh checkout prints "No .txt study resources found" and exits.
- The script loads its API key from the parent folder (`example langchain agents/.env`), which matches the README but not the module docstring (which says "shared repo-root .env"). It is also the opposite of the vibecoder example, which keeps `.env` in its own folder. No `.env` exists today.
- Retrieval may silently return nothing. The retriever uses a relevance threshold of 0.2 on a Chroma collection with the default L2 distance. For OpenAI's unit-length embeddings, that turns a cosine similarity of about 0.3 into a relevance of about 0.16, so a short topic like "Calvin cycle" could be filtered out. The model then writes its answer from "No relevant study context was found." and the learner sees a vague "this is missing" reply instead of a cheatsheet. This has not been checked against real embeddings.
- The Chroma and TextLoader integrations come from `langchain-community`, which now raises a sunset DeprecationWarning on import.

The project has no tests, so none of this was caught.

## Solution

A learner can follow the README top to bottom and generate a cheatsheet, summary, organised notes and a quiz from a bundled sample document on the first run, with no warnings and no crash. They can then drop in their own `.txt` notes. Retrieval reliably finds the relevant notes for a short topic. When it truly finds nothing, the learner is told so directly. A test suite proves the whole CLI works offline and, when a key is present, against OpenAI.

## User Stories

1. As a learner, I want `pip install -r requirements.txt` to install versions the script works with, so that a future LangChain release does not break the workshop again.
2. As a learner, I want the script to start without an import error on current LangChain, so that I reach the menu.
3. As a learner, I want the script to start without deprecation warnings, so that I am not confused about whether something is broken.
4. As a learner, I want one clear place to put my `.env`, stated identically in the README, the `.env.example` comment and the module docstring, so that I do not guess.
5. As a learner, I want the `.env` location to follow the same convention as the vibecoder example, so that the two examples feel consistent.
6. As a learner, I want a clear message naming the missing variable and the expected `.env` path when my API key is missing, so that I can fix it without reading a stack trace.
7. As a learner, I want a sample study document bundled in `documents/`, so that my first run produces real output before I add my own notes.
8. As a learner, I want the "no documents" message to show the folder path and that only `.txt` files load, so that I know exactly what to add.
9. As a learner, I want my own `.txt` files picked up alongside or instead of the sample, so that I can study my own material.
10. As a learner, I want files with non-ASCII characters (accents, symbols, smart quotes) to load, so that real notes do not crash the loader.
11. As a learner, I want a short topic such as "Calvin cycle" to retrieve the matching notes, so that the generated resource is grounded in my documents.
12. As a learner, I want to be told plainly when no notes match my topic, so that I can rephrase the topic instead of reading a vague answer.
13. As a learner, I want to choose a resource by number or by name, so that the menu is forgiving.
14. As a learner, I want an invalid menu choice to re-show the menu with a hint, so that a typo does not end my session.
15. As a learner, I want an empty topic to be rejected with a prompt to retry, so that I do not waste an API call.
16. As a learner, I want the cheatsheet to contain definitions, formulas, dates and memory cues from my notes, so that it is useful for revision.
17. As a learner, I want the summary to fit on about one page, so that it is a quick read.
18. As a learner, I want the organised notes to use headings and bullets, so that they are easy to scan.
19. As a learner, I want the quiz to end with an answer key, so that I can mark myself.
20. As a learner, I want later requests to remember earlier ones in the same session, so that I can ask follow-ups like "now quiz me on that".
21. As a learner, I want `exit` to quit cleanly, so that I can end a session whenever I like.
22. As a learner, I want the script to keep working when stdin closes (piped input or Ctrl-D), so that it exits instead of showing an EOFError trace.
23. As a workshop instructor, I want an offline test command that needs no API key, so that I can check the example in seconds before a session.
24. As a workshop instructor, I want a live test command that uses my `.env`, so that I can confirm the real OpenAI path works before a session.
25. As a maintainer, I want live tests skipped, not failed, when no key is set, so that the suite stays green on machines without a key.
26. As a maintainer, I want the README to list the test commands, so that contributors run them.

## Implementation Decisions

- **Imports:** move to LangChain 1.x module paths. Prompt templates, messages and output parsers come from `langchain-core`; the text splitter comes from `langchain-text-splitters`. A patched copy using exactly these paths ran end to end in this session.
- **Integrations:** replace `langchain-community`'s Chroma with the dedicated `langchain-chroma` package. Replace `TextLoader` with a small loader that reads each `.txt` file as UTF-8 and builds a Document with the file name as `source`, which drops the `langchain-community` dependency entirely. Keep the existing `load_study_documents()` interface: it returns a list of Documents, with metadata `{"source": <file name>}`.
- **Dependencies:** pin every package in requirements.txt to the versions verified in this session's venv (langchain-core 1.6.x, langchain-openai 1.7.x, langchain-text-splitters 1.1.x, chromadb 1.5.x, python-dotenv 1.2.x), plus `langchain-chroma` and `pytest`. Drop `langchain` and `langchain-community` if nothing else imports them.
- **`.env` location:** the script loads `.env` from its own folder (`study_langchain/.env`), matching vibecoder. Update the README setup step (`cp .env.example .env`), the docstring and the `.env.example` comment to say the same.
- **Missing key:** check for `OPENAI_API_KEY` at startup, before loading documents. If it is missing, print one line naming the variable and the expected `.env` path, then exit with a non-zero status.
- **Sample document:** ship one short sample `.txt` in `documents/`, real study content of about 2-3 chunks. The README explains that learners can replace or add to it.
- **Retrieval:** create the Chroma collection with cosine distance, so relevance scores track cosine similarity. Keep a threshold, but pick its value from a live check against the sample document: short topics drawn from the sample must clear it, and an unrelated topic must not. If the threshold filters out every chunk, `retrieve_context()` keeps returning the "no relevant context" marker, and `run_chat()` prints a direct message to the learner and skips the LLM call for that turn. Today the marker is passed to the model, which hides the problem.
- **Input handling:** `run_chat()` treats end-of-input from `input()` as `exit`.
- **Unchanged:** the four chains, their prompts, the models (`gpt-4o-mini`, `text-embedding-3-small`), the menu text, `route_choice()` and `format_chat_history()`. The offline run showed these work once the imports are fixed.

## Testing Decisions

- **One seam:** `run_chat()`, driven in-process. The test replaces `input()` with a scripted list of answers and captures stdout. Offline tests swap the module's `ChatOpenAI` and `OpenAIEmbeddings` for fakes. Live tests keep the real classes but subclass the chat model to record each prompt it sends. Each test points the documents folder at a temporary directory. No test reaches into the retriever or chains directly; this is the seam the offline probe in this session used successfully.
- **A good test** checks what the learner sees (menu, messages, the generated resource is printed) and what the model was sent (the context and the focus in the prompt). It does not check how chains are composed.
- **Offline cases (no key):**
  - each menu option, by number and by name, prints the fake model's reply under the right heading;
  - an invalid choice re-shows the menu;
  - an empty topic is rejected without a model call;
  - an empty documents folder prints the help message and makes no model call;
  - a non-ASCII document loads;
  - a missing key exits with the clear message;
  - closed stdin exits cleanly;
  - chat history from turn 1 appears in turn 2's prompt.
- **Live cases (key present, otherwise skipped):**
  - with the bundled sample, a short topic from the sample produces a prompt whose context contains a sample source, and the printed output is non-empty;
  - an unrelated topic prints the "no matching notes" message and makes no generation call.
- **Layout:** tests live under `tests/` in study_langchain, with a `live` marker. A short README section lists `pytest -m "not live"` and `pytest -m live`.
- **Prior art:** the vibecoder example's e2e suite (now deleted from the working tree, still in git history) used the same approach: a fake LLM swapped in at module level, a live marker skipped without a key, and `.env` loaded in conftest.

## Out of Scope

- Loading file types other than `.txt`, such as PDF, Markdown or Word.
- Persisting the vector store between runs.
- Saving generated resources to files.
- Changing prompt wording, models, or the menu's set of resources.
- Trimming or summarising chat history as it grows.
- Any change to the vibecoder example or the lodge_project folder.

## Further Notes

- **Verification gap:** the retrieval threshold concern is an analysis, not an observation. No API key was available in this session: the only `.env` was in the vibecoder folder, which has since been removed from the working tree. The user will add a `.env` with a real key for testing. Run the live check first when implementing.
- **Session artifacts:** a `.venv` was created in study_langchain during this session. Python's venv marks it as git-ignored.
