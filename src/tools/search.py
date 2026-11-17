from langchain_tavily import TavilySearch
from src.config import TAVILY_API_KEY

# Initialize Tavily Search Tool
def get_search_tool():
    '''
    Initialize the Tavily Search Tool.
    '''
    return TavilySearch(max_results=2, api_key=TAVILY_API_KEY)

