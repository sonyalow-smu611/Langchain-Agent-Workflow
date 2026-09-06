# Vibecoder LangChain Agent

Vibecoder is a teaching example for a LangChain + LangGraph multi-agent coding workflow. It takes a product request, creates structured planning output, builds technical contracts, runs frontend/backend worker agents, checks tests, and shows where repair and human review fit.

## Setup

From the repo root:

```bash
cd "example langchain agents/vibecoder"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create your local environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4.1-mini
HITL=0
```

`MODEL_NAME` is optional. `HITL=1` pauses the workflow before repair when QA creates repair tickets.

## Run

The runnable workshop file is in `run_vibecoder/`:

```bash
python run_vibecoder/vibecoder_langchain.py
```

The script makes real OpenAI calls. Keep the virtual environment active and make sure `.env` exists in the `vibecoder/` folder before running it.

## Use

The runner uses the sample request inside `run_vibecoder/vibecoder_langchain.py`:

```python
USER_REQUEST = """
Build a simple task management application.
...
"""
```

To try a different app idea, edit `USER_REQUEST` and run the file again.

During a run, the script prints each workshop section:

1. What are we building?
2. LLM
3. Agent
4. Tools
5. Structured output
6. State
7. Full LangGraph workflow

The final output prints the state keys, QA status, and repair attempt count. Generated demo files are written under `workspace/`.

## Project Map

`run_vibecoder/`

Contains `vibecoder_langchain.py`, the main file to run. It is a commented walkthrough that imports the real project modules and wires the workshop flow together.

`src/agents/`

Agent functions. `director.py` turns a request into product and task plans. `architect.py` creates the technical blueprint, schema, and API contract. `frontend.py` and `backend.py` generate proposed implementation changes. `qa_repair.py` turns test failures into repair tickets and asks the LLM for fixes.

`src/graph/`

LangGraph workflow pieces. `state.py` defines the shared workflow state. `nodes.py` adapts agent functions into graph nodes. `graph.py` shows the smaller reference graph. `routing.py` decides whether QA should end or route to repair.

`src/prompts/`

Markdown system prompts for each agent. Edit these when you want to change how an agent reasons or formats output.

`src/schemas/`

Pydantic models used for structured LLM output and typed state, including product specs, tasks, architecture, API contracts, database schemas, test reports, and repair tickets.

`src/tools/`

Small local tools used by the workflow. `filesystem.py` reads and writes files inside `workspace/`. `testing.py` runs pytest and returns a structured test report. `artifacts.py` saves and loads JSON artifacts. `git.py` and `search.py` are placeholders for source-control and search-style tool work.

`src/resources/`

Reference guidance for generated applications: architecture rules, coding standards, API/database conventions, design system notes, security guidance, and testing guidance.

`examples/`

Static example input and example run notes for readers who want to understand the intended workflow before running it.

`tests/`

Pytest checks for schemas and tools.

`workspace/`

Sandbox folder for files generated or read by the local tools. The runner may create `workspace/workshop_note.txt`.

`pyproject.toml`

Project metadata and pytest configuration.

`.env.example`

Template for local environment variables. Copy it to `.env`.

`requirements.txt`

Python packages needed to run `run_vibecoder/vibecoder_langchain.py` and the tests.
