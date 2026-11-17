import streamlit as st
from groq import RateLimitError

from src.agent import build_agent

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
    if submitted and user_query.strip():
        if user_query.strip():
            try:
                with st.spinner("Checking the sky..."):
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
            except RateLimitError:
                st.warning("Rate limit reached. Please wait a few seconds and try again.")
        else:
            st.warning("Add a question first, then ask your weather scout.")


if __name__ == '__main__':
    run_agent_ui()