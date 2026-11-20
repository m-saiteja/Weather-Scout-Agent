import pytest
from langchain.tools import tool
from src.agent import build_agent


pytestmark = pytest.mark.integration


@tool('weather')
def mock_weather(location: str) -> str:
    """
    Get the current weather in a given city/location.
    """
    return f"Mock weather data for {location}: 20°C, sunny"


@tool('tavily_search')
def mock_search(query: str) -> str:
    '''
    Search the web for current events or information.
    '''
    return f'Mock search results for: {query}'


@pytest.fixture
def agent():
    return build_agent(tools=[mock_weather, mock_search])


def extract_tools_calls(messages):
    '''
    Helper function to extract all tool calls from the agent's
    message history.
    '''
    return [
        call 
        for msg in messages
        if hasattr(msg, "tool_calls") and msg.tool_calls
        for call in msg.tool_calls
    ]


def test_routes_to_weather_tool(agent):
    '''
    Test that the agent routes to the weather tool 
    ONLY for weather queries
    '''
    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "What's the weather like in Hyderabad today?"
                }
            ]
        },
        config={"configurable": {"thread_id": "test_routing_weather"}}
    )
    tool_calls = extract_tools_calls(response["messages"])

    # Assert atlease one tool was called
    assert len(tool_calls) >= 1

    # Assert that the called tool is the weather tool
    tool_names = [call["name"] for call in tool_calls]
    assert "weather" in tool_names

    # Assert the location argument was extracted correctly
    weather_call = next(call for call in tool_calls if call["name"]=="weather")
    assert "Hyderabad" in weather_call["args"]["location"]


def test_routes_to_seach_tools(agent):
    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "What is the current stock price of Nvidia?"
                }
            ]
        },
        config={"configurable": {"thread_id": "test_routing_search"}}
    )
    tool_calls = extract_tools_calls(response["messages"])
    print(f"Hey:{tool_calls}")

    assert len(tool_calls) >= 1
    tool_names = [call["name"] for call in tool_calls]

    # Assert it picked search, and did NOT call weather
    assert "tavily_search" in tool_names
    assert "weather" not in tool_names

    search_call = next(call for call in tool_calls if call["name"]=="tavily_search")
    assert "stock price of Nvidia" in search_call["args"]["query"]


def test_conversational_query_uses_no_tools(agent):
    response = agent.invoke(
        {
            "messages": [{"role": "user", "content": "Hello! How are you doing today?"}]
        },
        config={"configurable": {"thread_id": "test_routing_chat"}}
    )
    
    tool_calls = extract_tools_calls(response["messages"])
    
    # Assert zero tools were triggered
    assert len(tool_calls) == 0
    
    # Assert a natural-language response was still generated
    final_message = response["messages"][-1].content
    assert len(final_message.strip()) > 0
