# qwen3-coder:30b
from typing import Dict, Any
from langchain_ollama.chat_models import ChatOllama
from langchain.messages import AIMessage
from evocore.model.model_manager import BaseModel


class QwenCode(BaseModel):
    name = "qwen_code_local"

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self.model = ChatOllama(model="qwen3-coder:30b")

    def invoke(self, prompt: str, max_tokens: int = 100) -> AIMessage:
        return self.model.invoke(prompt)
