from typing import TypedDict
from langchain_ollama.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts import architect_prompt, format_instructions
from time import time

# system_prompt = architect_prompt.format(format_instructions=format_instructions)
human_prompt = "generate the project architecture according to the requirement of the user: {description}"


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

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", architect_prompt),
        ("human", human_prompt),
    ]
).partial(format_instructions=format_instructions)

description = "this is a code agent, deploy on the GCP's cloud run, using langgraph as the agent base platform, using fastapi for the backend."

chain = prompt | llms["gemma"] | StrOutputParser()
resp = chain.invoke({"description": description})

print(resp)

# for name in llms:
#     state = time()
#     chain = prompt | llms[name] | StrOutputParser
#     chain.invoke({"description": description})
