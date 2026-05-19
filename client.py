import asyncio

from langchain_core.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import OllamaLLM
from models import llm

SERVERS = {
    "Demo Server": {
        "transport": "stdio",
        "command": "/opt/homebrew/bin/uv",
        "args": [
            "run",
            "fastmcp",
            "run",
            "/Users/raaggee/Documents/mcp_sample/main.py",
        ],
    }
}


async def main():
    print("Started MCP Server")
    client = MultiServerMCPClient(SERVERS)

    tools = await client.get_tools()
    # print(tools)
    named_tools = {}
    for tool in tools:
        named_tools[tool.name] = tool

    llm_with_tools = llm.bind_tools(tools)

    prompt = "Find all the expenses."

    response = await llm_with_tools.ainvoke(prompt)
    print(response)

    if not getattr(response, "tool_calls", None):
        print(f"Final Answer: {response.content}")
        return

    print(f"LLM Result: {response.tool_calls}")

    tool_messages = []
    for tc in response.tool_calls:
        tool_selected = response.tool_calls[0]["name"]
        tool_args = response.tool_calls[0]["args"]
        tool_id = response.tool_calls[0]["id"]
        tool_res = await named_tools[tool_selected].ainvoke(tool_args)
        tool_messages.append(ToolMessage(content=tool_res, tool_call_id=tool_id))

    final_ans = await llm_with_tools.ainvoke([prompt, response, *tool_messages])
    print(f"Final Answer: {final_ans.content}")


if __name__ == "__main__":
    asyncio.run(main())
