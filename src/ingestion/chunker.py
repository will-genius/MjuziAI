import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class SmartChunker:
    def __init__(self,chunk_size=1000, chunk_overlap=150):
        self.chunk_size= chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter= RecursiveCharacterTextSplitter(
            chunk_size= self.chunk_size,
            chunk_overlap= self.chunk_overlap,
            separators= ["\n\n","\n","."," ",""]
        )
    
    def chunk_documents(self, documents):
        chunked_docs = self.text_splitter.split_documents(documents)
        return chunked_docs
    

if __name__== "__main__":
    doc_short= Document(
        page_content="Swahili Word: rafiki | Definition: A person with whom one shares companionship.",
        metadata={"source": "kamusi", "type": "short"}
    )

    long_text = "Equity Bank 2026 HR Policy. " * 50 + "Employees must report at 8 AM. " * 50 + "Paternity leave is 14 days. " * 50
    doc_long = Document(
        page_content=long_text,
        metadata={"source": "equity_bank_policy.pdf", "type": "long"}
    )

    test_documents = [doc_short, doc_long]

    print("--- Initializing Smart Chunker ---")
    chunker = SmartChunker(chunk_size=100, chunk_overlap=20) 
    results = chunker.chunk_documents(test_documents)
    print("--- Output Preview ---")
    for i, chunk in enumerate(results[:10]): # Preview the first 3 chunks
        print(f" Chunk {i+1} (Source: {chunk.metadata['source']})")
        print(f"Text: {chunk.page_content[:100]}...")
        print(f"Length: {len(chunk.page_content)} characters")
