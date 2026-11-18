import json
import pytest
from pathlib import Path
from langchain.tools import tool

from src.agent import build_agent


@tool("weather")
def mock_weather(location: str) -> str:
    """
    Get the current weather for a given city/location.
    """
    # Simulate an invalid location error
    if "nonexistent" in location.lower() or "invalid" in location.lower():
        return f"Error: Unable to fetch weather data for {location}. Status code: 400"
    return f"Mock weather data for {location}: 22°C, partly cloudy, humidity 60%"


@tool("tavily_search")
def mock_search(query: str) -> str:
    """
    Search the web for current events, facts, and general information.
    """
    return f"Mock search results for: {query}."


@pytest.fixture(scope="module")
def agent():
    return build_agent(tools=[mock_weather, mock_search])


DATASET_PATH = Path(__file__).parent / "golden_dataset.json"
with open(DATASET_PATH, "r", encoding="utf-8") as f:
    GOLDEN_DATASET = json.load(f)


@pytest.mark.parametrize("case", GOLDEN_DATASET, ids=[case["id"] for case in GOLDEN_DATASET])
def test_agent_output_quality(agent, case):
    response = agent.invoke({
        "messages": [
            {
                "role": "user", 
                "content": case["input"]
            }
        ]
    })

    final_answer = response["messages"][-1].content

    # Assertion 1: Final answer must not be empty
    assert len(final_answer.strip()) > 0, "Agent returned an empty response!"

    # Assertion 2: Negative pattern check (No leaked JSON, tools, or reasoning)
    for pattern in case["forbidden_patterns"]:
        assert pattern.lower() not in final_answer.lower(), (
            f"Policy violation in test '{case['id']}': "
            f"Found forbidden text '{pattern}' in response:\n{final_answer}"
        )

    # Assertion 3: Brevity check (Adheres to 'short answer' prompt rule)
    word_count = len(final_answer.split())
    assert word_count <= case["max_words"], (
        f"Response too verbose in test '{case['id']}': "
        f"Expected <= {case['max_words']} words, but got {word_count} words."
    )

    # Assertion 4: Hallucination / Grounding Check
    if "required_keywords" in case:
        found_any = any(keyword.lower() in final_answer.lower() for keyword in case["required_keywords"])
        assert found_any, (
            f"Hallucination / Faithfulness failure in '{case['id']}': "
            f"Expected at least one of {case['required_keywords']} in response, but got:\n{final_answer}"
        )