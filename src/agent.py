from langchain_groq import ChatGroq
from langchain.agents import create_agent

from src.prompts import SYSTEM_PROMPT
from src.tools import get_weather, get_search_tool
from src.config import GROQ_API_KEY, MODEL_NAME, TEMPERATURE

# Create the agent
def build_agent(tools=None, llm=None):
    '''
    Build and return the agent with the specified tools and prompt.
    '''
    # LLM Initialization
    if llm is None:
        llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            max_retries=5
        )
    if tools is None:
        tools = [get_weather, get_search_tool()]

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        debug=False
    )
    