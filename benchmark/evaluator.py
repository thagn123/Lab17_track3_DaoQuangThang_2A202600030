import sys
import os
import time
import json
import pandas as pd
from tabulate import tabulate
from dotenv import load_dotenv

# Load API keys
load_dotenv()

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import MultiMemoryAgent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

class MemoryBenchmark:
    """
    Compares Agent with memory vs a vanilla LLM using cases from JSON.
    """
    def __init__(self, user_id: str, test_cases_path: str = "benchmark/test_cases.json"):
        self.user_id = user_id
        self.agent = MultiMemoryAgent(user_id)
        self.vanilla_llm = ChatOpenAI(model="gpt-4o-mini")
        self.test_cases_path = test_cases_path
        self.test_cases = self._load_test_cases()

    def _load_test_cases(self):
        try:
            with open(self.test_cases_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading test cases: {e}")
            return []

    def run(self):
        results = []
        print(f"Starting Benchmark with {len(self.test_cases)} cases...")
        
        for case in self.test_cases:
            category = case["category"]
            query = case["query"]
            print(f"Processing [{category}]: {query[:50]}...")

            # Agent with Memory
            start_time = time.time()
            agent_resp = self.agent.chat(query)
            agent_time = time.time() - start_time
            
            # Vanilla LLM
            start_time = time.time()
            vanilla_resp = self.vanilla_llm.invoke([HumanMessage(content=query)]).content
            vanilla_time = time.time() - start_time
            
            results.append({
                "Category": category,
                "Query": query,
                "With Memory": agent_resp,
                "Vanilla": vanilla_resp,
                "Time (s)": round(agent_time, 2)
            })
            
        self._save_report(results)
        self._save_debug_report() # New: Save memory debug info
        return results

    def _save_report(self, results):
        df = pd.DataFrame(results)
        report_path = "benchmark/benchmark_report.md"
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# 📊 Multi-Memory Agent Benchmark Report\n\n")
            f.write(f"**Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**User ID:** {self.user_id}\n\n")
            f.write("## Summary Table\n\n")
            # Create a shortened table for the file
            display_df = df.copy()
            display_df["With Memory"] = display_df["With Memory"].str[:100] + "..."
            display_df["Vanilla"] = display_df["Vanilla"].str[:100] + "..."
            f.write(tabulate(display_df, headers='keys', tablefmt='github', showindex=False))
            
            f.write("\n\n## Detailed Logs\n\n")
            for r in results:
                f.write(f"### Category: {r['Category']}\n")
                f.write(f"**Query:** {r['Query']}\n\n")
                f.write(f"**- Agent with Memory:**\n> {r['With Memory']}\n\n")
                f.write(f"**- Vanilla LLM:**\n> {r['Vanilla']}\n\n")
                f.write("---\n\n")
        
        print(f"\nSUCCESS: Benchmark complete! Report saved to: {report_path}")

    def _save_debug_report(self):
        """
        Dumps the internal state of all 4 memories into a debug Markdown file.
        """
        debug_path = "benchmark/memory_debug_report.md"
        ltm = self.agent.long_term
        epi = self.agent.episodic
        sem = self.agent.semantic
        
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write("# 🔍 Multi-Memory Debug Report\n\n")
            f.write("Giải thích chi tiết về dữ liệu đang được lưu trữ trong từng ngăn nhớ.\n\n")
            
            # 1. Long-term Memory (Redis/Fallback)
            f.write("## 1. Long-term Memory (User Facts & Preferences)\n")
            f.write("> **Nơi lưu:** Redis (hoặc Dictionary RAM nếu fallback). Dùng để cá nhân hóa lâu dài.\n\n")
            
            facts = ltm.get_user_facts(self.user_id)
            prefs = ltm.get_user_preferences(self.user_id)
            
            f.write("### 👤 User Facts\n")
            if facts:
                for fact in facts: f.write(f"- {fact}\n")
            else: f.write("*Trống*\n")
            
            f.write("\n### ⚙️ User Preferences\n")
            if prefs:
                f.write("| Key | Value |\n|---|---|\n")
                for k, v in prefs.items(): f.write(f"| {k} | {v} |\n")
            else: f.write("*Trống*\n")
            
            # 2. Episodic Memory (Experiences)
            f.write("\n## 2. Episodic Memory (Learning from Experience)\n")
            f.write("> **Nơi lưu:** ChromaDB. Dùng để nhớ lại cách giải quyết các vấn đề tương tự trong quá khứ.\n\n")
            
            # Retrieve all episodes (using a broad query)
            episodes = epi.retrieve_episodes(query="everything", top_k=5)
            if episodes:
                for idx, ep in enumerate(episodes):
                    f.write(f"### Episode {idx+1}: {ep['task']}\n")
                    f.write(f"- **Outcome:** {ep['outcome']}\n")
                    f.write(f"- **Reflection:** *{ep['reflection']}*\n")
                    f.write(f"- **Importance Score:** {ep.get('importance', 'N/A')}\n")
                    f.write(f"- **Trajectory Snapshot:** {str(ep['trajectory'])[:150]}...\n\n")
            else: f.write("*Trống*\n")

            # 3. Semantic Memory (Knowledge)
            f.write("\n## 3. Semantic Memory (RAG Knowledge)\n")
            f.write("> **Nơi lưu:** ChromaDB. Dùng để lưu trữ kiến thức chuyên môn hoặc tài liệu thực tế.\n\n")
            
            # For demo, we search common terms
            knowledge = sem.query_knowledge(query="French Revolution", top_k=2)
            if knowledge:
                for kn in knowledge:
                    f.write(f"- **Content:** {kn['content'][:200]}...\n")
                    f.write(f"  - **Source:** {kn['metadata'].get('source', 'Unknown')}\n")
            else: f.write("*Trống - Bạn có thể nạp thêm kiến thức qua hàm add_knowledge*\n")

            # 4. Short-term Memory (Chat History)
            f.write("\n## 4. Short-term Memory (Current Context)\n")
            f.write("> **Nơi lưu:** Python List (Buffer). Giúp Agent hiểu ngữ cảnh của vài câu chat gần nhất.\n\n")
            f.write(f"Agent đang duy trì phiên chat với User ID: `{self.user_id}`.\n")
            f.write("Cơ chế: Sliding window (Tự động cắt tỉa khi vượt quá giới hạn Token).\n")

        print(f"DEBUG: Debug report saved to: {debug_path}")

if __name__ == "__main__":
    # Ensure you are in the project root when running
    benchmark = MemoryBenchmark(user_id="test_user_999")
    benchmark.run()
