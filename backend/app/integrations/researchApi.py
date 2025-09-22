from langchain_tavily import TavilySearch
from langchain_community.tools import DuckDuckGoSearchRun
from app.utils.config import TAVILY_API_KEY

tavily_client = TavilySearch()
duck_duck_go_client = DuckDuckGoSearchRun()

# print(duck_duck_go_client.invoke("Who is Donald Trump ?"))
# print(tavily_client.invoke("Who is Donald Trump ?"))