from google import genai
from google.genai import types
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

    contents = []
    for m in chat_history:
        contents.append(types.Content(role=m["role"], parts=[types.Part.from_text(text=m["content"])]))
    tools = types.Tool(function_declarations=tools)
    config = types.GenerateContentConfig(tools=[tools] if use_tools else None)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=config
    )


    return response


def ask_real_estate_agent(property_info: str, MAX_TOOL_CALLS: int = 3) -> str:
    print("Real estate agent in action....")
    user_prompt = DEVELOPMENT_OPPORTUNITIES_PROMPT.replace("[PROPERTY_INFO]", property_info)
    chat_history = [
        {"role": "user", "content": "You are an expert real estate developer assistant. Do nor "},
        {"role": "user", "content": user_prompt}
    ]
    response = ask_llm(chat_history)
    tool_calls = 0
    while response.candidates[-1].content.parts[-1].function_call and tool_calls < MAX_TOOL_CALLS:
        print("Tool call detected....")
        function = response.candidates[-1].content.parts[-1].function_call
        tool_name = function.name
        tool_args = function.args
        chat_history.append({"role": "model", "content": f"Calling tool: {tool_name} with args: {tool_args}"})
        tool_result = globals()[tool_name](**tool_args)
        chat_history.append({"role": "user", "content": tool_result + f"\n\nYou have {MAX_TOOL_CALLS - tool_calls} tool calls left."})
        tool_calls += 1
        response = ask_llm(chat_history)
    print("Answer incoming....")
    response = ask_llm(chat_history, use_tools=False)
    return response.candidates[-1].content.parts[-1].text

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

    # chat_history = [
    #     {"role": "user", "content": "You are an expert real estate developer assistant. Use the tools provided to you to answer the user's question."},
    #     {"role": "user", "content": property_info}
    # ]


    response = ask_real_estate_agent(property_info)
    print("="*100)
    print(response)
    