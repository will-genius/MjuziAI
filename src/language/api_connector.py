import os

class LanguageConnector:
    
    def __init__(self, api_key: str = None, mock_mode: bool = True):
        self.api_key = api_key
        self.mock_mode = mock_mode
        
        if not self.mock_mode and not self.api_key:
            raise ValueError("API Key is required if not running in mock mode.")
            
        # In a production environment, you would initialize the OpenAI/Vambo client here
        # import openai
        # self.client = openai.OpenAI(api_key=self.api_key)

    def detect_language(self, text: str) -> str:
        """
        Analyzes a text block and returns its primary language.
        """
        if self.mock_mode:
            # Simple mock logic for testing without an API key
            if "the" in text.lower() or "is" in text.lower():
                return "English"
            return "Swahili/Sheng"
            
        # Real API Call would look like this:
        # response = self.client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages=[{"role": "system", "content": "Detect the language. Reply with ONLY the language name."},
        #               {"role": "user", "content": text}]
        # )
        # return response.choices[0].message.content.strip()

    def translate_to_english(self, text: str) -> str:
        """
        Translates Swahili or Sheng into standard English.
        """
        if self.mock_mode:
            return f"[MOCK TRANSLATION: {text}]"
            
        # Real API Call logic here...
        pass

    def standardize_sheng(self, text: str) -> str:
        """
        Cleans up code-switched Sheng/Swahili into formal Swahili or English 
        so the Vector Database can index it accurately.
        """
        if self.mock_mode:
            return f"[MOCK STANDARDIZED SHENG for: {text[:20]}...]"
        
        # Real API Call logic here...
        pass

# ==========================================
# DAY 5 TEST EXECUTION
# ==========================================
if __name__ == "__main__":
    print("--- Initializing Language API Connector ---")
    
    # We run in Mock Mode so it works instantly on your laptop today
    connector = LanguageConnector(mock_mode=True)
    
    sample_sheng = "Ninaeza chukua paternity leave ya days ngapi?"
    sample_english = "How many paternity leave days am I entitled to?"
    
    print("Testing Language Detection:")
    print(f"Text 1: '{sample_sheng}' -> Detected: {connector.detect_language(sample_sheng)}")
    print(f"Text 2: '{sample_english}' -> Detected: {connector.detect_language(sample_english)}")
    
    print("\n Testing Translation Layer:")
    print(f"Original: {sample_sheng}")
    print(f"English Translation: {connector.translate_to_english(sample_sheng)}")
    
    print("\nLanguage API wrapper successfully configured.")