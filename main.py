
import os
import sys
import argparse
import subprocess

import certifi
import requests
import streamlit as st
from dotenv import load_dotenv

from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain.agents import create_agent

os.environ['SSL_CERT_FILE'] = certifi.where()

load_dotenv()
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')


# Initialize Tavily Search Tool
SEARCH_TOOL = TavilySearch(max_results=2, api_key=TAVILY_API_KEY)


# Define the weather tool
@tool("weather")
def get_weather(location: str) -> str:
    """
    Get the current weather for a given city/location.
    """
    url = f"https://api.weatherapi.com/v1/current.json"
    response = requests.get(
            url,
            params={"key": WEATHER_API_KEY, "q": location},
            timeout=30
        )
    if response.status_code == 200:
        data = response.json()
        return data
    return (
        f"Error: Unable to fetch weather data for {location}."
        f"Status code: {response.status_code}"
    )


# Tools List
TOOLS = [SEARCH_TOOL, get_weather]


# Prompt Template
PROMPT = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Reply to the user with a short, natural-language answer only.
Do not show your reasoning, tool calls, or raw tool output.
"""


# Create the agent
def build_agent():
    '''
    Build and return the agent with the specified tools and prompt.
    '''
    # LLM Initialization
    llm = ChatGroq(api_key=GROQ_API_KEY, model="openai/gpt-oss-20b", temperature=0)
    return create_agent(
        model=llm,
        tools=TOOLS,
        system_prompt=PROMPT,
        debug=False
    )


@st.cache_resource
def get_agent():
    '''
    Streamlit re-runs this script on every interaction;
    caching avoids rebuilding the agent each time.
    '''
    return build_agent()


# Streamlit App Configuration
def run_agent_ui():
    '''
    Run the Streamlit UI for the agent.
    '''
    st.set_page_config(
        page_title="Weather scout",
        page_icon=":material/partly_cloudy_day:",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    st.title("Your weather & web scout", icon=":material/partly_cloudy_day:")
    st.markdown(
        "A little sky sense, a little web search — all in one place."
    )

    with st.container(horizontal=True):
        st.badge("Live weather", icon=":material/cloud:", color="blue")
        st.badge("Web search", icon=":material/travel_explore:", color="green")

    weather_col, search_col = st.columns(2)
    with weather_col.container(border=True, height="stretch"):
        st.subheader("Check the sky", icon=":material/wb_sunny:")
        st.caption("Current conditions for cities around the world.")
        st.caption('Try: “What’s the weather in Tokyo?”')
    with search_col.container(border=True, height="stretch"):
        st.subheader("Explore the web", icon=":material/travel_explore:")
        st.caption("Find useful answers and bring them together with the forecast.")
        st.caption('Try: “What’s the capital of India and its weather?”')

    st.subheader("What would you like to know?", icon=":material/search:")
    with st.container(border=True):
        with st.form("weather_agent_search", border=False):
            query_col, submit_col = st.columns(
                [5, 1], vertical_alignment="bottom"
            )
            with query_col:
                user_query = st.text_input(
                    "Your question",
                    placeholder="Ask about a forecast, a place, or anything to search…",
                )
            with submit_col:
                submitted = st.form_submit_button(
                    "Ask",
                    icon=":material/arrow_forward:",
                    type="primary",
                    width="stretch",
                )
    agent = build_agent()
    if submitted:
        if user_query.strip():
            agent_response = agent.invoke({
                "messages": [{
                    "role": "user", 
                    "content": user_query.strip()}]
            })
            st.markdown("#### Your answer")
            with st.chat_message(
                "assistant", avatar=":material/partly_cloudy_day:"
            ):
                st.write(agent_response["messages"][-1].content)
        else:
            st.warning("Add a question first, then ask your weather scout.")


def run_cli():
    '''
    Run the agent in CLI mode.
    '''
    agent = build_agent()
    print("Weather Scout (type 'exit', 'quit' or 'bye' to leave)")
    while True:
        user_input = input("Enter your question: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            break
        agent_response = agent.invoke({
                                "messages": [{
                                    "role": "user", 
                                    "content": user_input}]
                        })
        print(f"Agent Response: {agent_response['messages'][-1].content}")


def running_under_streamlit() -> bool:
    '''
    Check if the script is running under Streamlit.
    '''
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
 
        return get_script_run_ctx(suppress_warning=True) is not None
    except Exception:
        return False


def main():
    '''
    Main function to run the Weather Scout Agent.
    '''
    if running_under_streamlit():
        run_agent_ui()
        return

    # CLI Interface through argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
                    "--cli", 
                    action="store_true",
                    help="Run the Weather Scout Agent in CLI?"
                )
    args = parser.parse_args()
    print(f"Running in CLI mode?: {args.cli}")
    if args.cli:
        run_cli()
    else:
        # sys.executable makes Streamlit run in the SAME environment as this script
        subprocess.run([sys.executable, "-m", "streamlit", "run", os.path.abspath(__file__)])


if __name__ == "__main__":
    main()
