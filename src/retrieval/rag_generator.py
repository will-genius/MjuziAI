import os
import sys
from dotenv import load_dotenv

# Safely import the OpenAI chat model
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

# Load the .env file so we can securely access the API key when needed
load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.append(src_dir)
sys.path.append(os.path.join(src_dir, "database"))

from database.vector_vault import VectorVault

class RAGGenerator:
    def __init__(self, mock_mode: bool = True):
        print("Initializing RAG generator...")
        
        # CRITICAL: We pass use_openai=False so it reads from the local database
        # where we just stored the 1024-dimension BAAI chunks!
        self.vault = VectorVault(use_openai=False)
        self.db = self.vault.get_database()
        self.mock_mode = mock_mode

        if not self.mock_mode:
            if ChatOpenAI is None:
                raise ImportError("langchain_openai is missing. Run: pip install langchain-openai")
                
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("Production Mode requires a valid OPENAI_API_KEY in your .env file!")
                
            print("🔌 Connecting to OpenAI GPT-4o-mini...")
            # We use gpt-4o-mini because it is incredibly smart, fast, and cheap
            self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.2)
        
    def _build_prompt(self, question: str, context_chunks: list) -> str:
        context_text = "\n\n".join([doc.page_content for doc in context_chunks])
        prompt = f"""
        You are MjuziAI, an intelligent and polite enterprise assistant.
        Answer the user's question ONLY using the exact information provided in the Context below.
        If the context does not contain the answer, reply exactly with: "I do not have information on that in my current knowledge base."
        
        CONTEXT:
        {context_text}
        
        QUESTION: {question}
        
        ANSWER:
        """
        return prompt
    
    def generate_answers(self, query: str, collection_name: str) -> str:
        print(f"\n Searching vault for: '{query}'...")
        results = self.db.similarity_search(
            query=query,
            k=5, # We grab 5 chunks to ensure we get both dictionary definitions AND proverbs
            filter={"collection_name": collection_name}
        )

        if not results:
            return " No information found in this collection."
        
        print(" Compiling context and formatting prompt...")
        prompt = self._build_prompt(
            question=query,
            context_chunks=results
        )

        # Extract unique sources for our citations
        sources = [doc.metadata.get("doc_name") for doc in results]
        unique_sources = list(set(sources))

        if self.mock_mode:
            print(" Running in MOCK MODE (No API key charged)...")
            mock_answer = (
                f"Based on the provided context, here is what I found regarding '{query}'.\n"
                f"Top raw context pulled: {results[0].page_content.split('|')[0].strip()}...\n"
                f"\n Sources consulted: {', '.join(unique_sources)}"
            )
            return mock_answer
            
        # REAL LLM CALL (When you top up your OpenAI account)
        print(" Generating AI response...")
        response = self.llm.invoke(prompt)
        
        # We append the citations perfectly at the end of the AI's response
        final_output = f"{response.content}\n\n Sources consulted: {', '.join(unique_sources)}"
        return final_output

if __name__ == "__main__":
    # We keep it in True for now so you don't get 429 quota errors!
    rag = RAGGenerator(mock_mode=True)
    
    print("\n==================================================")
    print("    MJUZIAI RAG GENERATOR (TERMINAL CHAT)")
    print("   Type 'exit' to close.")
    print("==================================================")
    
    while True:
        user_query = input("\n👤 You: ").strip()
        
        if user_query.lower() == "exit":
            print("Shutting down chat window. Goodbye!")
            break
            
        final_response = rag.generate_answers(
            query=user_query,
            collection_name="TUKI_Kamusi"
        )

        print(f"\n MjuziAI:\n{final_response}")