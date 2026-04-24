from typing import List
from langchain_core.messages import BaseMessage, trim_messages

class ShortTermMemory:
    """
    Handles conversation history with token-based trimming.
    """
    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens

    def get_messages(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        Trims messages to fit within the token limit, keeping the system message.
        """
        return trim_messages(
            messages,
            max_tokens=self.max_tokens,
            strategy="last",
            token_counter=len, # Simplified for demo, usually uses tiktoken
            include_system=True,
            allow_partial=False,
        )
