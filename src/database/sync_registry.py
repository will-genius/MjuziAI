import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(current_dir, ".."))

from database.vector_vault import VectorVault

def sync_collections():
    print("Initiating Enterprise Registry Sync...")
    vault = VectorVault(use_openai=False)
    db = vault.get_database()
    
    total_count = db._collection.count()
    print(f"Found {total_count} total chunks in ChromaDB. Scanning safely in batches...")
    
    batch_size = 500
    collections = {}

    # Read the database in safe batches to prevent memory crashes
    for i in range(0, total_count, batch_size):
        data = db._collection.get(include=['metadatas'], limit=batch_size, offset=i)
        
        for meta in data['metadatas']:
            if not meta: continue
            c_name = meta.get('collection_name')
            if not c_name: continue
            
            if c_name not in collections:
                collections[c_name] = {
                    "name": c_name,
                    "visibility": meta.get("visibility", "public"),
                    "org_id": meta.get("organization_id", "public_domain"),
                    "chunk_count": 0,
                    "doc_names": set()
                }
                
            collections[c_name]["chunk_count"] += 1
            if meta.get("doc_name"):
                collections[c_name]["doc_names"].add(meta.get("doc_name"))

    # Format the data
    registry = {}
    for c_name, data in collections.items():
        data["doc_count"] = len(data["doc_names"])
        del data["doc_names"] # Remove the set before saving to JSON
        registry[c_name] = data
        print(f"Found Collection: {c_name} ({data['chunk_count']} chunks)")

    # Save to JSON
    registry_file = os.path.join(project_root, "collections_registry.json")
    with open(registry_file, "w") as f:
        json.dump(registry, f, indent=4)
        
    print(f"\n Sync Complete! The JSON registry has been rebuilt and saved to {registry_file}.")

if __name__ == "__main__":
    sync_collections()