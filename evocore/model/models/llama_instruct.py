# llama3:instruct
from typing import Dict, Any
from langchain_ollama.chat_models import ChatOllama
from langchain.messages import AIMessage
from evocore.model.model_manager import BaseModel


class Llama(BaseModel):
    name = "llama-instruct-local"

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.model = ChatOllama(model="llama3:instruct")

    def invoke(self, prompt: str, max_tokens: int = 100) -> AIMessage:
        return self.model.invoke(prompt)
