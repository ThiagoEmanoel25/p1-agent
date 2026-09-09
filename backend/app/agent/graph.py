from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START 
from langgraph.graph.message import MessagesState
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from .tools import get_weather

tools = [get_weather]

model = ChatOpenAI(
        model_name="gpt-4.1-mini",
        temperature=0,
)

model_with_tools = model.bind_tools(tools)


async def call_model(state: MessagesState):
    response = await model_with_tools.ainvoke(state ["messages"])

    return {
        "messages": [response]
    }


def create_graph() -> CompiledStateGraph:
    builder = StateGraph(MessagesState)

    builder.add_node(
        "model",
        call_model,
    )

    builder.add_node(
        "tools",
        ToolNode(tools),
    )

    builder.add_edge(
        START,
        "model",
    )

    builder.add_conditional_edges(
        "model",
        tools_condition,
    )

    builder.add_edge(
        "tools",
        "model",
    )

    return builder.compile()
