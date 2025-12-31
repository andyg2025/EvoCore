# gemma3:27b
from typing import Dict, Any
from langchain_ollama.chat_models import ChatOllama
from langchain.messages import AIMessage
from evocore.model.model_manager import BaseModel


class Gemma12(BaseModel):
    name = "gemma3_27b_local"

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.model = ChatOllama(model="gemma3:27b")

    def invoke(self, prompt: str, max_tokens: int = 100) -> AIMessage:
        return self.model.invoke(prompt)
