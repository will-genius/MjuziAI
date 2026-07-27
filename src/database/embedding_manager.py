from langchain_huggingface import HuggingFaceEmbeddings

class EmbeddingManager:
    def __init__(self, model_name:str="intfloat/multilingual-e5-small"):
        print(f"Initializing Embedding Model:{model_name}")

        self.embedder= HuggingFaceEmbeddings(model_name = model_name)

    def get_embedder(self):
        return self.embedder
    
#Test code
if __name__=="__main__":
    print("Testing multilingual embeddding model")

    manager= EmbeddingManager()
    embedder= manager.get_embedder()

    test_sentence_english = "What are the rules of the bank?"
    test_sentence_swahili = "Sheria za benki ni nini?"

    english_vector= embedder.embed_query(test_sentence_english)
    swahili_vector= embedder.embed_query(test_sentence_swahili)

    print(f"English vector: first 5 of {len(english_vector)}coordinates: {english_vector[:5]}")
    print(f"swahili vector: first 5 of {len(swahili_vector)}coordinates: {swahili_vector[:5]}")
