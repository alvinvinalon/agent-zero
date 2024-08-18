import os
import requests
from agent import Agent
from . import online_knowledge_tool
from python.helpers import perplexity_search
from python.helpers import duckduckgo_search

from . import memory_tool
import concurrent.futures

from python.helpers.tool import Tool, Response
from python.helpers import files
from python.helpers.print_style import PrintStyle

class BingSearchTool(Tool):
    def execute(self, question="", **kwargs):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Schedule the two functions to be run in parallel

            # perplexity search, if API provided
            # if os.getenv("API_KEY_PERPLEXITY"):
            #     perplexity = executor.submit(perplexity_search.perplexity_search, question)
            # else: 
            #     PrintStyle.hint("No API key provided for Perplexity. Skipping Perplexity search.")
            #     perplexity = None

            # # duckduckgo search
            # duckduckgo = executor.submit(duckduckgo_search.search, question)

            # bing search
            bing = executor.submit(self.bing_search, question)

            # memory search
            future_memory = executor.submit(memory_tool.search, self.agent, question)

            # Wait for all functions to complete
            # perplexity_result = (perplexity.result() if perplexity else "") or ""
            # duckduckgo_result = duckduckgo.result()
            bing_result = bing.result()
            memory_result = future_memory.result()

        msg = files.read_file("prompts/tool.knowledge.response.md", 
                                      online_sources=str(bing_result),
                                      memory=memory_result)

        if self.agent.handle_intervention(msg): pass # wait for intervention and handle it, if paused

        return Response(message=msg, break_loop=False)

    def bing_search(self, query):
        api_key = os.getenv("BING_API_KEY")
        if not api_key:
            PrintStyle.hint("No API key provided for Bing. Skipping Bing search.")
            return ""

        headers = {"Ocp-Apim-Subscription-Key": api_key}
        params = {"q": query, "textDecorations": True, "textFormat": "HTML"}
        response = requests.get("https://api.bing.microsoft.com/v7.0/search", headers=headers, params=params)
        response.raise_for_status()
        search_results = response.json()

            # Extracting relevant information from search results
        results = []
        for result in search_results.get("webPages", {}).get("value", []):
            results.append({
                "name": result.get("name"),
                "url": result.get("url"),
                "snippet": result.get("snippet")
            })
        return results