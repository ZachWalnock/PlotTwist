from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
from prompts import DEVELOPMENT_OPPORTUNITIES_PROMPT
from main import get_enhanced_parcel_data
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
    property_info = get_enhanced_parcel_data("", "263", "N Harvard", "St", "")
    print(property_info)

    # response = ask_real_estate_agent(property_info)
    # print("="*100)
    # print(response)
    