import os
import requests

def bing_search(query: str, api_key=None, base_url="https://api.bing.microsoft.com/v7.0/search"):
    api_key = api_key or os.getenv("BING_API_KEY")
    if not api_key:
        raise ValueError("No API key provided for Bing Search.")

    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": query, "textDecorations": True, "textFormat": "HTML"}
    response = requests.get(base_url, headers=headers, params=params)
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