from typing import List, Optional, TypedDict

from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph

from backend.ai.tools.github import github_repo
from backend.ai.tools.invoice import invoice_parser
from backend.ai.tools.weather import weather_data


class GenerativeUIState(TypedDict, total=False):
    input: HumanMessage
    result: Optional[str]
    """Plain text response if no tool was used."""
    tool_calls: Optional[List[dict]]
    """A list of parsed tool calls."""
    tool_result: Optional[dict]
    """The result of a tool call."""


def invoke_model(state: GenerativeUIState, config: RunnableConfig) -> GenerativeUIState:
    tools_parser = JsonOutputToolsParser()
    initial_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是一个有用的助手。您将获得工具列表以及用户的输入.\n"
                # + "Your job is to determine whether or not you have a tool which can handle the users input, or respond with plain text.",
                + "你的工作是确定你是否拥有可以处理用户输入或以纯文本响应的工具。",
            ),
            MessagesPlaceholder("input"),
        ]
    )
    model = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True)
    tools = [github_repo, invoice_parser, weather_data]
    model_with_tools = model.bind_tools(tools)
    chain = initial_prompt | model_with_tools
    result = chain.invoke({"input": state["input"]}, config)

    if not isinstance(result, AIMessage):
        raise ValueError("Invalid result from model. Expected AIMessage.")

    if isinstance(result.tool_calls, list) and len(result.tool_calls) > 0:
        parsed_tools = tools_parser.invoke(result, config)
        print("parsed_tools", parsed_tools)

        print("parsed_tools", parsed_tools)
        return {"tool_calls": parsed_tools}
    else:
        print("result.content", result.content)
        return {"result": str(result.content)}


def invoke_tools_or_return(state: GenerativeUIState) -> str:
    if "result" in state and isinstance(state["result"], str):
        return END
    elif "tool_calls" in state and isinstance(state["tool_calls"], list):
        return "invoke_tools"
    else:
        raise ValueError("Invalid state. No result or tool calls found.")


def invoke_tools(state: GenerativeUIState) -> GenerativeUIState:
    tools_map = {
        "github-repo": github_repo,
        "invoice-parser": invoice_parser,
        "weather-data": weather_data,
    }

    if state["tool_calls"] is not None:
        tool = state["tool_calls"][0]
        selected_tool = tools_map[tool["type"]]
        return {"tool_result": selected_tool.invoke(tool["args"])}
    else:
        raise ValueError("No tool calls found in state.")


def create_graph() -> CompiledGraph:
    workflow = StateGraph(GenerativeUIState)

    workflow.add_node("invoke_model", invoke_model)  # type: ignore
    workflow.add_node("invoke_tools", invoke_tools)

    # Add a conditional edge from the starting node to any number of destination nodes.
    # 添加从起始节点到任意数量的目标节点的条件边。
    workflow.add_conditional_edges("invoke_model", invoke_tools_or_return)

    # 指定要在图中调用的第一个节点。
    workflow.set_entry_point("invoke_model")

    # 将节点标记为图形的终点
    workflow.set_finish_point("invoke_tools")

    # 将状态图编译为 CompiledGraph 对象。
    graph = workflow.compile()
    return graph
