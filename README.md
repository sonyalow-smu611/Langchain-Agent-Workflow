# Langchain-Agent-Workflow

User Request
     │
     ▼
 Director Agent
     │
     ▼
 Architect / Schema Agent
     │
     ├──────────────┐
     ▼              ▼
 FE Worker       BE Worker
     │              │
     └──────┬───────┘
            ▼
        QA / Repair
            │
       ┌────┴────┐
       │         │
     PASS       FAIL
       │         │
       ▼         ▼
      END      REPAIR
                  │
                  └──────► QA


# Langgraph 
                 ┌───────────────┐
                 │ LangGraph     │
                 │ Orchestration │
                 └───────┬───────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
     Agents            Tools            State
        │                │                │
     Reasoning        Actions        Communication

multi-agent-coding-workflow/
│
├── README.md
│
├── pyproject.toml
├── requirements.txt
├── .env.example
│
├── src/
│   ├── agents/
│   │   ├── director.py
│   │   ├── architect.py
│   │   ├── frontend.py
│   │   ├── backend.py
│   │   └── qa_repair.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   ├── graph.py
│   │   ├── routing.py
│   │   └── nodes.py
│   │
│   ├── tools/
│   │   ├── filesystem.py
│   │   ├── testing.py
│   │   ├── browser.py
│   │   └── git.py
│   │
│   ├── schemas/
│   │   ├── product.py
│   │   ├── architecture.py
│   │   ├── tasks.py
│   │   └── testing.py
│   │
│   ├── prompts/
│   │   ├── director.md
│   │   ├── architect.md
│   │   ├── frontend.md
│   │   ├── backend.md
│   │   └── qa_repair.md
│   │
│   └── resources/
│       ├── coding_standards.md
│       ├── architecture_rules.md
│       ├── design_system.md
│       ├── testing_guidelines.md
│       └── security_guidelines.md
│
├── examples/
│   ├── example_request.md
│   └── example_run.md
│
├── tests/
│
└── notebooks/
    └── workshop_model_answer.ipynb

# Teaching Progression 

01_single_agent/
02_structured_output/
03_tools/
04_shared_state/
05_two_agent_handoff/
06_parallel_workers/
07_conditional_routing/
08_self_healing_loop/
09_human_in_loop/
10_full_workflow/

