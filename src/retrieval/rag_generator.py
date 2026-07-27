import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.append(src_dir)
sys.path.append(os.path.join(src_dir, "database"))

from database.vector_vault import VectorVault

class RAGGenerator:
    def __init__(self,api_key:str=None, mock_mode:str=True):
        print("Initializing Rag generator")
        self.vault= VectorVault()
        self.db= self.vault.get_database()
        self.mock_mode= mock_mode
        self.api_key= api_key

        if not self.mock_mode and not self.api_key:
            raise ValueError("Production Mode requires a valid LLM API Key!")
        
    def _build_prompt(self,question:str,context_chunks:list)->str:
        context_text= "\n\n".join([doc.page_content for doc in context_chunks])
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
    
    def generate_answers(self, query:str, collection_name:str)->str:
        print(f"searching vault for :{query}")
        results= self.db.similarity_search(
            query= query,
            k=3,
            filter= {"collection_name":collection_name}
        )

        if not results:
            return "No information found in this collection"
        
        print("compiling context and sending to the llm")
        prompt= self._build_prompt(
            question=query,
            context_chunks=results
        )

        #mock llm behavior
        if self.mock_mode:
            print("Runing in mock mode")
            sources=[doc.metadata.get("doc_name") for doc in results]
            unique_sources= list(set(sources))
            mock_answer = (
                f"Based on the provided context, here is what I found regarding '{query}'.\n"
                f"The dictionary entries define related concepts such as: {results[0].page_content.split('|')[0].strip()}.\n"
                f"\n[Sources consulted: {', '.join(unique_sources)}]"
            )
            return mock_answer
        ## Real LLM Call would go here 

#test code
if __name__=="__main__":
    rag= RAGGenerator(mock_mode=True)
    print("   MJUZIAI RAG GENERATOR (TERMINAL CHAT)")
    print("   Type 'exit' to close.")
    while True:
        user_query= input("Query is:").strip()
        if user_query.lower() == "exit":
            print("Shutting down chat window")
            break
        final_response= rag.generate_answers(
            query=user_query,
            collection_name="TUKI_Kamusi"
        )

        print(f"{final_response}")


