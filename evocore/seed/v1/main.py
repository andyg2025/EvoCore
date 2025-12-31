from time import time
from typing import List, TypedDict, Annotated
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langgraph.graph import StateGraph, END


ARCHITECT_SYSTEM_PROMPT = """
You are a senior software architect.

Your task:
- Design a production-ready project structure.
- Focus on clarity and simplicity.
- Do NOT write any code.
- Think from the perspective of a code generation agent.

The output will be consumed by another agent that generates code strictly
based on your specification.

{format_instructions}
"""

ARCHITECT_HUMAN_PROMPT = """
User requirement:
{description}
"""

CODER_SYSTEM_PROMPT = """
You are a senior software engineer.

Your task:
- Generate complete, correct code.
- Follow the architecture specification EXACTLY.
- Do NOT invent new files or change responsibilities.
- Each file must be self-contained and runnable.

Output format:
For each file, output:

FILE: <path>
<full code>

Do not include explanations.
"""

CODER_HUMAN_PROMPT = """
Architecture specification:
{architecture_json}
"""


class FileSpec(BaseModel):
    path: str
    description: str
    responsibilities: str


class ArchitectureSpec(BaseModel):
    project_name: str
    project_type: str
    tech_stack: dict
    global_requirements: List[str]
    files: List[FileSpec]


llms = {
    "llama_it": ChatOllama(model="llama3:instruct"),
    "llama": ChatOllama(model="llama3.1:8b"),
    "gemma27": ChatOllama(model="gemma3:27b"),
    "gemma12": ChatOllama(model="gemma3:12b"),
    "gemma": ChatOllama(model="gemma3:latest"),
    "gpt": ChatOllama(model="gpt-oss:20b"),
    "qwen": ChatOllama(model="qwen3:30b"),
    "qwen_code": ChatOllama(model="qwen3-coder:30b"),
}


llm_arch = llms["gpt"]
llm_code = llms["qwen_code"]


class AgentState(TypedDict):
    description: str
    architecture: ArchitectureSpec | None
    code: str | None


def architect_agent(state: AgentState) -> dict:
    state_time = time()

    parser = PydanticOutputParser(pydantic_object=ArchitectureSpec)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", ARCHITECT_SYSTEM_PROMPT),
            ("human", ARCHITECT_HUMAN_PROMPT),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    chain = prompt | llm_arch | parser

    architecture = chain.invoke({"description": state["description"]})

    end_time = time()
    print(f"architect agent using time: {end_time-state_time}")
    print(f"architecture: {architecture}")

    return {"architecture": architecture}


def coder_agent(state: AgentState) -> dict:
    state_time = time()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CODER_SYSTEM_PROMPT),
            ("human", CODER_HUMAN_PROMPT),
        ]
    )

    chain = prompt | llm_code | StrOutputParser()

    code = chain.invoke({"architecture_json": state["architecture"].json()})

    end_time = time()
    print(f"architect agent using time: {end_time-state_time}")
    print(f"code: {code}")

    return {"code": code}


builder = StateGraph(AgentState)

builder.add_node("architect", architect_agent)
builder.add_node("coder", coder_agent)

builder.set_entry_point("architect")
builder.add_edge("architect", "coder")
builder.add_edge("coder", END)

graph = builder.compile()

# if __name__ == "__main__":
#     description = (
#         "Build a simple code generation agent service. "
#         "Deployable on GCP Cloud Run. "
#         "Use FastAPI as backend."
#     )

#     result = graph.invoke({"description": description})

#     print("\n====== GENERATED CODE ======\n")
#     print(result["code"])


if __name__ == "__main__":
    description = (
        "Build a simple code generation agent service. "
        "Deployable on GCP Cloud Run. "
        "Use FastAPI as backend."
    )

    # Use stream instead of invoke
    # The 'stream_mode' can be "updates" (default) or "values"
    print("--- Starting Agent Workflow ---\n")

    stream_iterator = graph.stream({"description": description}, stream_mode="updates")

    final_result = {}

    for event in stream_iterator:
        for node_name, state_update in event.items():
            print(f"\n>>> Finished Node: {node_name} <<<")

            # If you want to see the JSON architecture as soon as it's ready:
            if node_name == "architect":
                print(f"Plan created: {state_update['architecture'].project_name}")

            # Store the state update to access the final code at the end
            final_result.update(state_update)

    print("\n====== FINAL GENERATED CODE ======\n")
    # Access the 'code' key from the accumulated result
    if "code" in final_result:
        print(final_result["code"])
