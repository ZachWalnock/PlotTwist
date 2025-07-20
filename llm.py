from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
from prompts import DEVELOPMENT_OPPORTUNITIES_PROMPT, GET_SIMILAR_DEVELOPMENT_PROMPT
from main import get_enhanced_parcel_data, format_property_data_for_llm
from tavily import TavilyClient
load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def web_search(**kwargs) -> str:
    result = tavily_client.search(query=kwargs["query"], max_results=3)
    urls = [r["url"] for r in result["results"]]
    content = "\n".join([r["content"] for r in result["results"]])
    print(result)
    return {"urls": urls, "content": content}


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
        config=config if use_tools else None
    )


    return response


def ask_real_estate_agent(prompt: str, MAX_TOOL_CALLS: int = 10) -> str:
    print("Real estate report in action...")
    chat_history = [
        {"role": "user", "content": "You are an expert real estate developer assistant. Do not use the first person, and format the promt as if it was being sent directly to the real estate developer."},
        {"role": "user", "content": prompt}
    ]
    response = ask_llm(chat_history)
    tool_calls = 0
    evidence = []
    while response.candidates[-1].content.parts[-1].function_call and tool_calls < MAX_TOOL_CALLS:
        print("Tool call detected....")
        function = response.candidates[-1].content.parts[-1].function_call
        tool_name = function.name
        tool_args = function.args
        chat_history.append({"role": "model", "content": f"Calling tool: {tool_name} with args: {tool_args}"})
        tool_result = globals()[tool_name](**tool_args)
        chat_history.append({"role": "user", "content": tool_result["content"] + f"\n\nYou have {MAX_TOOL_CALLS - tool_calls - 1} tool calls left."})
        evidence.extend(tool_result["urls"])
        tool_calls += 1
        response = ask_llm(chat_history)
    print("Answer incoming....")
    response = ask_llm(chat_history, use_tools=False)
    return {"content": response.candidates[-1].content.parts[-1].text, "evidence": evidence}

def get_similar_developments(formatted_property_info) -> str:
    user_prompt = GET_SIMILAR_DEVELOPMENT_PROMPT.replace("[PROPERTY_INFO]", formatted_property_info)
    return ask_real_estate_agent(user_prompt)

def get_estate_report(formatted_property_info: str, recent_developments_report: str) -> str:
    user_prompt = DEVELOPMENT_OPPORTUNITIES_PROMPT.replace("[PROPERTY_INFO]", formatted_property_info).replace("[RECENT_DEVELOPMENTS]", recent_developments_report)
    chat_history = [{"role": "user", "content": user_prompt}]
    response = ask_llm(chat_history, use_tools=False)
    return response.candidates[-1].content.parts[-1].text

if __name__ == "__main__":
    formatted_property_info = format_property_data_for_llm(get_enhanced_parcel_data("", "263", "N Harvard", "St", ""))
    recent_developments = get_similar_developments(formatted_property_info)
    with open("recent_developments.md", "w", encoding="utf-8") as f:
        f.write(recent_developments["content"])
    
    user_prompt = DEVELOPMENT_OPPORTUNITIES_PROMPT.replace("[PROPERTY_INFO]", formatted_property_info).replace("[RECENT_DEVELOPMENTS]", recent_developments["content"])
    report = get_estate_report(formatted_property_info, recent_developments["content"])
    print(report)
    report = report.candidates[-1].content.parts[-1].text
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report)
    with open("evidence.md", "w", encoding="utf-8") as f:
        f.write("\n".join(recent_developments["evidence"]))
    
    print(report)

    # response = ask_real_estate_agent(property_info)
    # print("="*100)
    # print(response)
    