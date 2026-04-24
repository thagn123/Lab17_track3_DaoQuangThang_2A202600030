import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory.semantic import SemanticMemory

load_dotenv()

def seed_semantic():
    print("--- Seeding Semantic Memory ---")
    sem = SemanticMemory()
    
    knowledge_path = "knowledge_base.txt"
    if not os.path.exists(knowledge_path):
        print(f"Error: {knowledge_path} not found.")
        return

    with open(knowledge_path, "r", encoding="utf-8") as f:
        content = f.read()
        # Split by sections defined by [Title]
        sections = content.split("\n\n")
        
        for section in sections:
            if section.strip():
                # Extract title as source
                title = "General Knowledge"
                if section.startswith("["):
                    end_idx = section.find("]")
                    title = section[1:end_idx]
                    section_content = section[end_idx+1:].strip()
                else:
                    section_content = section.strip()
                
                # Silently add to memory to avoid terminal encoding issues
                sem.add_knowledge(content=section_content, source=title)

    print("SUCCESS: Semantic Memory seeded successfully!")

if __name__ == "__main__":
    seed_semantic()
