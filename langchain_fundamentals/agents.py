"""
Classic LangChain ReAct agent: one tool (get_system_time) + a prompt pulled
from LangChain Hub, run through create_react_agent + AgentExecutor.

Run: `python agents.py` (needs OPENAI_API_KEY, plus internet access since it
     pulls the ReAct prompt from LangChain Hub at runtime).

Learn: the @tool decorator, hub.pull(), create_react_agent + AgentExecutor,
       and verbose=True to watch the agent's Thought/Action/Observation loop.

Compare to: langchain_workshop.ipynb section 5, which builds an agent the
newer, simpler way with langgraph's create_react_agent (no hub, no prompt
template to write).
"""

from pathlib import Path

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
import datetime
from langchain.agents import tool

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

@tool
def get_system_time(format: str = "%Y-%m-%d %H:%M:%S"):
    """ Returns the current date and time in the specified format """

    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime(format)
    return formatted_time

llm = ChatOpenAI(model="gpt-4")

query = "What is the current time in London? (You are in Singapore). Just show the current time and not the date"

prompt_template = hub.pull("hwchase17/react")

tools = [get_system_time]

agent = create_react_agent(llm, tools, prompt_template)

# verbose to see agent thinking process
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

agent_executor.invoke({"input": query})

