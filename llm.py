from google import genai
from dotenv import load_dotenv
import os
import json
from prompts import DEVELOPMENT_OPPORTUNITIES_PROMPT
import sys
from tavily import TavilyClient
load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def web_search(**kwargs) -> str:
    result = tavily_client.search(query=kwargs["query"], max_results=3)
    return "\n".join([r["content"] for r in result["results"]])


def ask_llm(chat_history: list[dict[str, str]], use_tools: bool = True) -> str:
    with open("tools.json", "r") as f:
        tools = json.load(f)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Explain bubble sort to me.",
    )


    return response


def ask_real_estate_agent(property_info: str, MAX_TOOL_CALLS: int = 3) -> str:
    user_prompt = DEVELOPMENT_OPPORTUNITIES_PROMPT.replace("[PROPERTY_INFO]", property_info)
    chat_history = [
        {"role": "system", "content": "You are an expert real estate developer assistant."},
        {"role": "user", "content": user_prompt}
    ]
    response = ask_llm(chat_history)
    print("="*100)
    print(response)
    tool_calls = 0
    while response.choices[-1].finish_reason == "tool_calls" and tool_calls < MAX_TOOL_CALLS:
        print("="*100)
        print("message", response.choices[-1].message)
        function = response.choices[-1].message.tool_calls[-1].function
        tool_name = function.name
        tool_args = json.loads(function.arguments)
        chat_history.append({"role": "assistant", "content": f"Calling tool: {tool_name} with args: {tool_args}"})
        tool_result = globals()[tool_name](**tool_args)
        chat_history.append({"role": "user", "content": tool_result + f"\n\nYou have {MAX_TOOL_CALLS - tool_calls} tool calls left."})
        tool_calls += 1
        response = ask_llm(chat_history)
    response = ask_llm(chat_history, use_tools=False)
    return response.choices[-1].message.content

if __name__ == "__main__":
    property_info = """## 1. Parcel Overview

- **Parcel ID:** 2201486000
- **Address:** 263 N Harvard St, Allston, MA 02134
- **Lot Size:** 11,525 sq ft
- **Existing Structure:** 3,539 sq ft, Two-Family Dwelling (6 beds, 3 baths, 2 kitchens)
- **Year Built:** 1890
- **Parking:** 7 spaces
- **Owner:** THE HELPING HAND TRUST
- **Owner Mailing Address:** 316 N Harvard St, c/o James Georges, Allston MA 02134

## 2. Zoning Information

- **Zoning District:** 2F-5000 (Two-Family Residential)
- **Zoning Code Source:** Article 51 (Allston-Brighton Neighborhood District)
- **Zoning Map:** Available at [BPDA Zoning Viewer](https://maps.bostonplans.org/zoningviewer/)
- **Allowed Use (By-Right):** 2-family residential structure
- **Overlay:** None reported

## 3. Dimensional Requirements (Article 51)

- **Max Height:** 35 ft
- **Min Lot Area:** 5,000 sq ft per dwelling unit
- **Min Lot Width:** 50 ft
- **Front Setback:** Typically 10–20 ft
- **FAR:** Approx. 0.5–0.6 (varies by parcel)"""

    chat_history = [
        {"role": "system", "content": "You are an expert real estate developer assistant."},
        {"role": "user", "content": "Whats goign on in the news?"}
    ]


    response = ask_llm("")
    print("="*100)
    print(response)
    