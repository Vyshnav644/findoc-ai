import os
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START, END

import config
from tools import TOOLS

model = ChatGoogleGenerativeAI(
    model=config.MODEL_NAME,
    google_api_key=os.getenv("GEMINI_API_KEY"),
    max_retries=2,
).bind_tools(TOOLS)

TOOLS_BY_NAME = {t.name: t for t in TOOLS}

SYSTEM = SystemMessage(content="""You are FinDoc AI, an assistant for a UAE accountant.
Use the invoice_database tool for questions about the company's own invoices.
Use the vat_guide tool for questions about UAE VAT rules. Some questions need both tools.
Answer only from tool results, never from memory.
When you use the VAT guide, cite the section and page, and mention it is the June 2018 guide.
Amounts are in AED. If a tool asks a clarifying question, ask the user that question.
If neither tool can help, say you can answer questions about invoices or UAE VAT rules.""")

def call_agent(state):
    response = model.invoke([SYSTEM] + state["messages"])
    return {"messages": [response]}


def call_tools(state):
    last = state["messages"][-1]
    results = []
    for tool_call in last.tool_calls:
        print("  [using tool:", tool_call["name"], "]")
        tool = TOOLS_BY_NAME[tool_call["name"]]
        output = tool.invoke(tool_call["args"])
        results.append(ToolMessage(content=output, tool_call_id=tool_call["id"]))
    return {"messages": results}

def should_continue(state):
    if state["messages"][-1].tool_calls:
        return "tools"
    return END


graph = StateGraph(MessagesState)
graph.add_node("agent", call_agent)
graph.add_node("tools", call_tools)
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, ["tools", END])
graph.add_edge("tools", "agent")
app = graph.compile(checkpointer=MemorySaver())

def message_text(message):
    if isinstance(message.content, str):
        return message.content
    return "".join(part.get("text", "") for part in message.content if isinstance(part, dict))


if __name__ == "__main__":
    chat = {"configurable": {"thread_id": "accountant-1"}}

    while True:
        question = input("You: ")
        if question.lower() == "exit":
            break

        try:
            result = app.invoke({"messages": [HumanMessage(content=question)]}, chat)
        except Exception as error:
            print("FinDoc: something went wrong (", type(error).__name__, "), please try again.")
            print()
            continue

        print("FinDoc:", message_text(result["messages"][-1]))
        print()