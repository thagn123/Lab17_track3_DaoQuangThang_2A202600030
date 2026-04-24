from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class ExtractionResult(BaseModel):
    facts: List[str] = Field(default_factory=list, description="List of new facts about the user.")
    preferences: dict = Field(default_factory=dict, description="Dictionary of user preferences found.")
    reflection: str = Field(description="A concise reflection on how the task was handled.")
    importance: float = Field(default=0.5, description="Score from 0 to 1 indicating how useful this experience is.")

class MemoryExtractor:
    """
    Extracts structured memory updates from a conversation turn.
    """
    def __init__(self, model_name: str = "gpt-4o"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.structured_llm = self.llm.with_structured_output(ExtractionResult, method="function_calling")
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Analyze the interaction below. Extract new user facts and preferences.\n"
                       "CRITICAL: If the user corrects or changes a previous fact (e.g., 'Actually, I am allergic to X, not Y'), "
                       "you must extract the NEW fact to ensure the memory remains consistent and up-to-date.\n"
                       "Interaction:\n{interaction}"),
        ])

    def extract(self, interaction: str) -> ExtractionResult:
        chain = self.prompt | self.structured_llm
        return chain.invoke({"interaction": interaction})
