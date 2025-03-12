from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode 
from test_jupyter_ai_tools.toolset import structured_tools

class State(TypedDict):
    messages: list
    file_path: str

def make_default_agent(openai_key: str, model: str = "gpt-4-turbo"):
    memory = MemorySaver()
    llm = ChatOpenAI(api_key=openai_key, model=model, temperature=0)
    tools = structured_tools
    model_bound = llm.bind_tools(tools)
    tool_node = ToolNode(tools=tools)

    def notebook_editor_node(state):
        messages = state["messages"]
        file_path = state["file_path"]
        result = model_bound.invoke(messages)
        return {"messages": messages + [result], "file_path": file_path}

    def should_continue(state):
        last_message = state["messages"][-1]
        if "tool_calls" in last_message.additional_kwargs and last_message.additional_kwargs["tool_calls"]:
            return "continue"
        return "end"

    def call_tool(state):
        messages = state["messages"]
        file_path = state["file_path"]
        if not messages:
            print("❌ ERROR: No messages found in state.")
            return {"messages": messages, "file_path": file_path}
        last_message = messages[-1]
        print("CALLING TOOL: ", last_message.additional_kwargs["tool_calls"][0]["function"])
        if "tool_calls" not in last_message.additional_kwargs or not last_message.additional_kwargs["tool_calls"]:
            print("❌ ERROR: No tool calls found in last AIMessage.")
            return {"messages": messages, "file_path": file_path}
        tool_results = tool_node.invoke({"messages": messages})
        if isinstance(tool_results, dict):
            tool_results = tool_results.get("messages", [])
        return {"messages": messages + tool_results, "file_path": file_path}

    builder = StateGraph(State)
    builder.add_node("notebook_editor", notebook_editor_node)
    builder.add_node("call_tool", call_tool)
    builder.add_edge(START, "notebook_editor")
    builder.add_conditional_edges("notebook_editor", should_continue, {"continue": "call_tool", "end": END})
    builder.add_edge("call_tool", "notebook_editor")
    graph = builder.compile(checkpointer=memory)
    return graph