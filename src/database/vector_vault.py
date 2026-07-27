import os
from langchain_chroma import Chroma
from embedding_manager import EmbeddingManager

class VectorVault:
    def __init__(self):
        current_dir= os.path.dirname(os.path.abspath(__file__))
        project_root= os.path.dirname(os.path.dirname(current_dir))
        self.persist_directory= os.path.join(project_root,"chromadb")
        self.embedding_manager= EmbeddingManager()
        self.embedder= self.embedding_manager.get_embedder()
        self.db= Chroma(
            collection_name="mjuziai_master_vault",
            embedding_function=self.embedder,
            persist_directory=self.persist_directory
        )
        print(f" Vault online and permanently anchored at {self.persist_directory}")

    def get_database(self):
        return self.db
    
#Test Code
if __name__=="__main__":
    print("initializing chromadb")
    vault = VectorVault()
    db_instance = vault.get_database()
    current_docs = db_instance._collection.count()

    print(f" Current Vault Capacity: {current_docs} chunks stored.")

