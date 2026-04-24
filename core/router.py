from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class MemoryRoute(BaseModel):
    """
    Schema for memory routing decision.
    """
    target: Literal["user", "factual", "episodic", "none"] = Field(
        description="The memory type to retrieve based on user query intent."
    )
    reasoning: str = Field(description="Explanation for the choice.")

class MemoryRouter:
    """
    Determines which memory type to query based on the user's intent.
    """
    def __init__(self, model_name: str = "gpt-4o"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.structured_llm = self.llm.with_structured_output(MemoryRoute, method="function_calling")
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert memory router. Analyze the user query and decide which memory type is most relevant.\n"
                       "- 'user': Queries about user preferences, personal facts, or past user details.\n"
                       "- 'factual': General knowledge, facts, or data stored in documents.\n"
                       "- 'episodic': Queries about 'how to solve' something based on past experience or process trajectories.\n"
                       "- 'none': Simple greetings or general conversation."),
            ("human", "{query}")
        ])

    def route(self, query: str) -> MemoryRoute:
        chain = self.prompt | self.structured_llm
        return chain.invoke({"query": query})
