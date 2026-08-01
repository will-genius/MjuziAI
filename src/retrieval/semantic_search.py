import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.append(src_dir)
sys.path.append(os.path.join(src_dir, "database"))

from database.vector_vault import VectorVault

class SemanticSearcher:
    def __init__(self):
        self.vault = VectorVault()
        self.db= self.vault.get_database()

    def search(self,query:str,collection_name:str,top_k:int=3):
        print(f"querying db for {query}")
        print(f"only searching from {collection_name}")

        results= self.db.similarity_search(
            query= query,
            k= top_k,
            filter= {"collection_name":collection_name}
        )
        return results
    
# Test code
if __name__ == "__main__":
    searcher= SemanticSearcher()
    print("   MJUZIAI SEMANTIC SEARCH ENGINE ")
    print("   Type 'exit' to close the searcher.")
    while True:
        test_query= input("Enter Question:").strip()
        if test_query.lower() == "exit":
            print("Engine shutting down")
            break

        results = searcher.search(
            query=test_query, 
            collection_name="TUKI_Kamusi",
            top_k=5
        )
        print(" TOP MATCHES ")
        if not results:
            print(" No results found. Check your collection name ")
        else:
            for i, doc in enumerate(results):
                print(f"Match {i+1}:")
                print(f"TEXT: {doc.page_content[:200]}")
                print(f"SOURCE: {doc.metadata.get('doc_name')} (Page {doc.metadata.get('page_number')})")







