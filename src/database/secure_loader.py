import os
import sys
import time 

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)
sys.path.append(src_dir)
sys.path.append(os.path.join(src_dir, "ingestion"))

from ingestion.ingestion_pipeline import IngestionPipeline
from database.vector_vault import VectorVault




class SecureLoader:
    def __init__(self):
        print("Starting the loader")
        self.vault= VectorVault()
        self.db= self.vault.get_database()

    def ingest_in_batches(self, documents: list, batch_size: int = 500):
        total_docs= len(documents)
        print(f"\n Starting Enterprise Batch Injection for {total_docs} chunks...")
        print(f" Batch Size is: {batch_size} chunks per injection.")

        for i in range(0, total_docs,batch_size):
            batch= documents[i:i+batch_size]
            print(f"Embedding and injecting chunks {i + 1} to {i + len(batch)}")
            self.db.add_documents(batch)
            time.sleep(0.5)
        print("\n ALL batches successfully embedded and locked in the Vector Vault!")



#Test code
if __name__=="__main__":
    pipeline= IngestionPipeline()
    loader= SecureLoader()
    
    target_files = [
        "tashbihi_clean.json",
        "methali_clean.json",
        "vitendawili_clean.json",
        "tuki_sw_en_clean.json",
        "tuki_en_sw_clean.json"
    ]
    
    data_dir = os.path.join(project_root, "data_inputs", "public_knowledge")
    total_processed = 0

    print("\n INITIATING MULTI-FILE PIPELINE INGESTION...")

    for file_name in target_files:
        file_path = os.path.join(data_dir, file_name)
        
        if not os.path.exists(file_path):
            print(f"Skipping '{file_name}' - File not found.")
            continue
            
        print(f"\n==================================================")
        print(f"   PROCESSING FILE: {file_name}")
        print(f"==================================================")
        
        all_chunks= pipeline.process_document(
            file_path=file_path,
            collection_name="TUKI_Kamusi",
            doc_name=file_name,
            user_id="sys_admin_01",
            organization_id="public_domain",
            visibility="public"
        )

        if all_chunks:
            loader.ingest_in_batches(all_chunks, batch_size=500)
            total_processed += len(all_chunks)

    current_docs = loader.db._collection.count()
    print("\n==================================================")
    print(f" INGESTION COMPLETE!")
    print(f"New Chunks Processed Today: {total_processed}")
    print(f" The Vector Vault currently holds {current_docs} embedded chunks.")
    print("==================================================")


