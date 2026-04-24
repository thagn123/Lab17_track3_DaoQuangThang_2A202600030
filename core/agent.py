from typing import Annotated, TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from core.router import MemoryRouter
from core.context_builder import ContextBuilder
from utils.extraction import MemoryExtractor

class AgentState(TypedDict):
    messages: List[BaseMessage]
    user_id: str
    query: str
    context: str
    route: str
    response: str

class MultiMemoryAgent:
    def __init__(self, user_id: str):
        self.user_id = user_id
        # Initialize components
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.router = MemoryRouter()
        self.builder = ContextBuilder()
        self.extractor = MemoryExtractor()
        self.llm = ChatOpenAI(model="gpt-4o-mini")

        # Build Graph
        self.workflow = StateGraph(AgentState)
        self.workflow.add_node("route", self.route_query)
        self.workflow.add_node("retrieve", self.retrieve_memory)
        self.workflow.add_node("generate", self.generate_response)
        self.workflow.add_node("write_back", self.update_memory)

        self.workflow.set_entry_point("route")
        self.workflow.add_edge("route", "retrieve")
        self.workflow.add_edge("retrieve", "generate")
        self.workflow.add_edge("generate", "write_back")
        self.workflow.add_edge("write_back", END)
        
        self.app = self.workflow.compile()

    def route_query(self, state: AgentState):
        decision = self.router.route(state["query"])
        return {"route": decision.target}

    def retrieve_memory(self, state: AgentState):
        route = state["route"]
        query = state["query"]
        
        user_mem = ""
        epi_mem = ""
        sem_mem = ""

        if route == "user":
            facts = self.long_term.get_user_facts(self.user_id)
            prefs = self.long_term.get_user_preferences(self.user_id)
            user_mem = f"Facts: {facts}. Preferences: {prefs}"
        elif route == "episodic":
            episodes = self.episodic.retrieve_episodes(query)
            epi_mem = str(episodes)
        elif route == "factual":
            knowledge = self.semantic.query_knowledge(query)
            sem_mem = str(knowledge)

        context = self.builder.build(
            system_context="You are a helpful assistant with multi-memory capabilities.",
            user_memory=user_mem,
            episodic_memory=epi_mem,
            semantic_memory=sem_mem
        )
        return {"context": context}

    def generate_response(self, state: AgentState):
        prompt = f"{state['context']}\nUser: {state['query']}"
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {"response": response.content}

    def update_memory(self, state: AgentState):
        interaction = f"User: {state['query']}\nAgent: {state['response']}"
        extracted = self.extractor.extract(interaction)
        
        # Write-back to Redis
        for fact in extracted.facts:
            self.long_term.add_user_fact(self.user_id, fact)
        for k, v in extracted.preferences.items():
            self.long_term.set_user_preference(self.user_id, k, v)
            
        # Write-back to Episodic
        self.episodic.add_episode(
            task=state["query"],
            trajectory=[state["query"], state["response"]],
            outcome="Success", # Simplified
            reflection=extracted.reflection,
            importance=extracted.importance
        )
        return state

    def chat(self, user_query: str):
        result = self.app.invoke({"query": user_query, "user_id": self.user_id, "messages": []})
        return result["response"]
