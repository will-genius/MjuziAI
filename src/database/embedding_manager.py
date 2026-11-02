import os
from dotenv import load_dotenv

# Try importing both; don't break if one is missing
try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    OpenAIEmbeddings = None

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    HuggingFaceEmbeddings = None

load_dotenv()

class EmbeddingManager:
    """
    The Mathematical Translator for MjuziAI.
    Converts Swahili and English text into high-dimensional vector coordinates.
    """
    
    def __init__(self, use_openai: bool = True):
        self.use_openai = use_openai
        
        if self.use_openai:
            print(" Initializing Enterprise Embedding Model: OpenAI text-embedding-3-small...")
            if not OpenAIEmbeddings:
                raise ImportError(" langchain_openai not installed. Run: pip install langchain-openai")
                
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(" OPENAI_API_KEY not found in .env file! Switch use_openai=False to use local models.")
                
            self.embedder = OpenAIEmbeddings(
                model="text-embedding-3-small", 
                api_key=api_key
            )
            print(" OpenAI Embedding Model successfully connected!")
            
        else:
            # Upgrade from e5-small to BAAI/bge-m3 (State-of-the-Art Multilingual)
            local_model_name = "BAAI/bge-m3"
            print(f" Initializing High-Performance Local Model: {local_model_name}...")
            
            if not HuggingFaceEmbeddings:
                raise ImportError(" langchain_huggingface not installed. Run: pip install langchain-huggingface")
                
            self.embedder = HuggingFaceEmbeddings(
                model_name=local_model_name,
                # Force it to use GPU if you have one, otherwise fallback to CPU
                model_kwargs={'device': 'cpu'}, 
                encode_kwargs={'normalize_embeddings': True}
            )
            print(f"Local {local_model_name} Model successfully loaded!")

    def get_embedder(self):
        """Returns the active embedding model."""
        return self.embedder

# ==========================================
# TEST EXECUTION
# ==========================================
if __name__ == "__main__":
    # Change use_openai to False if you want to test the local BAAI/bge-m3 model
    manager = EmbeddingManager(use_openai=False)
    embedder = manager.get_embedder()
    
    # Test a quick translation mapping
    test_text = "Mtoto wa nyoka ni nyoka."
    vector = embedder.embed_query(test_text)
    
    print(f"\n Success! '{test_text}' converted to a vector with {len(vector)} dimensions.")