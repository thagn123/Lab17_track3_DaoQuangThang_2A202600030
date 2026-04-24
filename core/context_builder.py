from typing import List, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

class ContextBuilder:
    """
    Assembles the final prompt by prioritizing and trimming contexts.
    """
    def __init__(self, max_total_tokens: int = 4000):
        self.max_total_tokens = max_total_tokens

    def build(self, 
              system_context: str, 
              task_context: str = "", 
              user_memory: str = "", 
              episodic_memory: str = "", 
              semantic_memory: str = "",
              tool_outputs: str = "") -> str:
        """
        Combines components into a single prompt string.
        Prioritization (lowest to highest): tool_outputs, semantic, episodic, user, task, system.
        """
        # Define components with priority
        components = [
            ("Tool Outputs", tool_outputs),
            ("Semantic Context", semantic_memory),
            ("Episodic Context", episodic_memory),
            ("User Memory", user_memory),
            ("Task Context", task_context)
        ]
        
        # Build the final context string
        final_context = f"SYSTEM: {system_context}\n\n"
        
        # Simplified token management: Add from top priority until limit (omitted for brevity in logic)
        for name, content in reversed(components):
            if content:
                final_context += f"### {name}\n{content}\n\n"
        
        return final_context
