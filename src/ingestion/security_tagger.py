import os
import uuid
from datetime import datetime,timezone
from langchain_core.documents import Document

class SecurityTagger:
    def __init__(self):
        pass 

    def stamp_passports(self,documents:list[Document],collection_name:str,doc_name:str,user_id:str="sys_admin",organization_id:str="public_domain",visibility:str="public")->list[Document]:
        tagged_documents=[]
        document_id= f"doc_{str(uuid.uuid4())[:8]}"
        upload_timestamp= datetime.now(timezone.utc).isoformat()
        source_type= doc_name.split(".")[-1].lower() if"." in doc_name else "unknown"

        for doc in documents:
            old_meta= doc.metadata
            raw_page= old_meta.get("page",0)
            if isinstance(raw_page,int):
                page_number= str(raw_page+1) if "page" in old_meta else "1"
            else:
                page_number= str(raw_page)

            strict_metadata = {
                "chunk_id": f"chk_{str(uuid.uuid4())[:8]}",
                "document_id": document_id,
                "collection_name": collection_name,  
                "user_id": user_id,
                "organization_id": organization_id,
                "visibility": visibility,
                "doc_name": doc_name,
                "page_number": page_number,
                "source_type": source_type,
                "upload_timestamp": upload_timestamp
            }

            tagged_doc= Document(
                page_content=doc.page_content,
                metadata= strict_metadata
            )
            tagged_documents.append(tagged_doc)
        return tagged_documents
    
#test code
if __name__== "__main__":
    print(f"initializing security tagger")
    tagger= SecurityTagger()

    mock_public_chunk = Document(page_content="Article 1: All sovereign power belongs to the people of Kenya.", metadata={"page": 0})
    mock_private_chunk = Document(page_content="Safaricom Agent Manual: How to reverse M-Pesa.", metadata={"page": 12})
    
    # Tag constituiton as public
    public_docs = tagger.stamp_passports(
        documents=[mock_public_chunk], 
        collection_name="Kenyan_Constitution", 
        doc_name="constitution_2010.pdf",
        user_id="sys_admin",
        organization_id="public_domain",
        visibility="public"
    )
    
    # Tag safaricom data
    private_docs = tagger.stamp_passports(
        documents=[mock_private_chunk], 
        collection_name="Safaricom_Customer_Care", 
        doc_name="agent_manual_2026.pdf",
        user_id="safaricom_admin",
        organization_id="Safaricom_001",
        visibility="private"
    )

    print("Document 1 constituiton")
    for key, val in public_docs[0].metadata.items():
        print(f"  - {key}: {val}")

    print("safaricom policy")
    for key, val in private_docs[0].metadata.items():
        print(f"  - {key}: {val}")

