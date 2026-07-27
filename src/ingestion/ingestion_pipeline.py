import os
from chunker import SmartChunker
from security_tagger import SecurityTagger
from universal_loader import UniversalLoader

class IngestionPipeline:
    def __init__(self):
        self.chunker= SmartChunker()
        self.tagger= SecurityTagger()
    
    def process_document(self, file_path:str,collection_name:str,doc_name:str ,user_id:str,organization_id:str,visibility:str):
        print(f"Starting Pipeline for {doc_name}")
        print(f"Target collection {collection_name}")
        print(f"organisation:{organization_id}| user:{user_id}| Visibility:{visibility}")

        loader = UniversalLoader(file_path)
        try:
            raw_documents = loader.load_document()
        except AttributeError:
            raw_documents = loader.load_file()
        if not raw_documents:
            print("Pipeline could not load document")
            return None
        
        chunked_documents=self.chunker.chunk_documents(raw_documents)
        Tagged_chunks= self.tagger.stamp_passports(
            documents=chunked_documents,
            collection_name=collection_name,
            doc_name=doc_name,
            user_id=user_id,
            organization_id=organization_id,
            visibility=visibility
            )

        print(f"Pipeline complete yielded {len(Tagged_chunks)}")
        return Tagged_chunks
    
# Test code
if __name__=="__main__":
    pipeline= IngestionPipeline()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    kamusi_path = os.path.join(project_root, "data_inputs", "public_knowledge", "Kamusi.json")

    final_chunks= pipeline.process_document(
        file_path = kamusi_path,
        collection_name="TUKI_Kamusi_Dictionary",
        doc_name="Kamusi.json",
        user_id="sys_admin_01",
        organization_id="public_domain",
        visibility="public"
    )

    if final_chunks:
        print("Preview of the first chunk")
        print(f"content:{final_chunks[0].page_content[:150]}")
        print(f"Final Metadata")
        for key, value in final_chunks[0].metadata.items():
            print(f"  [{key}]: {value}")

        print("Phase 1 complete")