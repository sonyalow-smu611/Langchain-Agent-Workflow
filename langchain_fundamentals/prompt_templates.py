"""
The smallest possible LangChain example: build a ChatPromptTemplate with
variables, fill it in two different ways, and send it to the model.

Run: `python prompt_templates.py` (needs OPENAI_API_KEY in the shared
     repo-root .env).

Learn: ChatPromptTemplate.from_template() vs .from_messages(), and the
difference between calling .invoke() on a template (fills in the blanks) vs
on a model (sends the filled prompt to the LLM).
"""

from pathlib import Path

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

llm = ChatOpenAI(model="gpt-4")

template = "Write a {tone} email to {company} expressing interest in the {position} position, mentioning {skill} as a key strength. Keep it to 4 lines max"

prompt_template = ChatPromptTemplate.from_template(template)

prompt =  prompt_template.invoke({
    "tone": "energetic", 
    "company": "samsung", 
    "position": "AI Engineer", 
    "skill": "AI"
})

# Example 2: Prompt with System and Human Messages (Using Tuples)
messages = [
    ("system", "You are a comedian who tells jokes about {topic}."),
    ("human", "Tell me {joke_count} jokes."),
]

prompt_template = ChatPromptTemplate.from_messages(messages)
prompt = prompt_template.invoke({"topic": "lawyers", "joke_count": 3})
result = llm.invoke(prompt)
print(result)
