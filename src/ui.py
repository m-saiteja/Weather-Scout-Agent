import sys
import time
import streamlit as st
from pathlib import Path
from groq import RateLimitError
from langchain_core.messages import AIMessageChunk

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.agent import build_agent
from src.config import setup_logger, validate_config
from src.rate_limiter import SlidingWindowRateLimiter
from src.guardrails import validate_input, sanitize_output

logger = setup_logger(__name__)

@st.cache_resource
def get_agent():
    '''
    Streamlit re-runs this script on every interaction;
    caching avoids rebuilding the agent each time.
    '''
    return build_agent()


@st.cache_resource
def get_rate_limiter():
    return SlidingWindowRateLimiter(
        max_requests=5,
        window_seconds=60,
        min_cooldown=2.0,
    )


def generate_response(agent, query: str, thread_id: str, status=None):
    '''
    Streams tokens from agent in real time.
    Filters out empty tool call chunks and yields only visible text.
    '''
    config = {"configurable": {"thread_id": thread_id}}
    for chunk, metadata in agent.stream(
        {
            "messages": [{
                "role": "user",
                "content": query

            }]
        },
        config=config,
        stream_mode="messages"
    ):
        # if the agent calls a tool, show it in the status box
        if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks and status:
            tool_name = chunk.tool_call_chunks[0].get("name")
            if tool_name:
                display_name = "Weather API" if "weather" in tool_name else "Web Search"
                status.write(f"Scouting data using **{display_name}**...")
        
        # when the final message arrives, clear the status and stream words
        if isinstance(chunk, AIMessageChunk) and chunk.content:
            if status:
                status.update(label="Compiling your final answer...", state="complete", expanded=False)
                status = None
            yield chunk.content


# Streamlit App Configuration
def run_agent_ui():
    '''
    Run the Streamlit UI for the agent.
    '''
    try:
        validate_config()
    except ValueError as e:
        st.error(f'Configuration Error: {e}')
        st.stop()

    if "thread_id" not in st.session_state:
        import uuid
        st.session_state.thread_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []
        
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
        with st.form("weather_agent_search", border=False, clear_on_submit=True):
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
        
    if st.session_state.messages:
        st.markdown("#### Conversation")
        for msg in st.session_state.messages:
            avatar = ":material/partly_cloudy_day:" if msg["role"] == "assistant" else None
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])

    agent = build_agent()
    if submitted and user_query.strip():
        if user_query.strip():
            # rate limiting
            rate_limiter = get_rate_limiter()
            allowed, wait = rate_limiter.check_limit(st.session_state.thread_id)
            if not allowed:
                st.warning(f"Please wait {wait} seconds before making another request.")
                return
            
            # input guardrails
            is_safe, error_msg = validate_input(user_query.strip())
            if not is_safe:
                st.error(error_msg)
                return

            with st.chat_message("user"):
                st.write(user_query.strip())
            st.session_state.messages.append({"role": "user", "content": user_query.strip()})

            # st.markdown("#### Your Answer")
            with st.chat_message("assistant", avatar=":material/partly_cloudy_day:"):
                try:
                    logger.info(f"User query reveived: '{user_query}'")
                    start_time = time.time()
                    status = st.status("Fetching the data to answer your query", expanded=True)
                    raw_response = st.write_stream(
                                            generate_response(
                                                        agent, 
                                                        user_query.strip(),
                                                        thread_id=st.session_state.thread_id,
                                                        status=status)
                                        )
                    duration = time.time() - start_time
                    logger.info(f"Agent finished response in {duration:.2f}s")
                    # output guardrails
                    safe_response = sanitize_output(raw_response)
                    st.session_state.messages.append({"role": "assistant", "content": safe_response})
                except RateLimitError:
                    st.warning("Rate limit reached. Please wait a few seconds and try again.")
        else:
            st.warning("Add a question first, then ask your weather scout.")


if __name__ == '__main__':
    run_agent_ui()