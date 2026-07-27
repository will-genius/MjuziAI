import os
import re
import json

class VitendawiliParser:
    """
    Parser for the Vitendawili text you provided.
    Reads the text and structures it into JSON format.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path

    def clean_raw_text(self, text: str) -> list[str]:
        """Cleans the raw text, removing empty lines."""
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("Sehemu ya Pili:"):
                cleaned_lines.append(line_str)
        return cleaned_lines

    def parse(self) -> list[dict]:
        """Parses the text into structured vitendawili entries."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"❌ Raw file not found at: {self.file_path}")
            
        try:
            import docx
        except ImportError:
            raise ImportError("❌ The 'python-docx' library is missing! Run: pip install python-docx")
            
        # Extract text directly from the .docx file
        doc = docx.Document(self.file_path)
        raw_text = "\n".join([para.text for para in doc.paragraphs])
            
        lines = self.clean_raw_text(raw_text)
        entries = []
        current_entry = None
        
        for line in lines:
            # Match number, period, riddle, hyphen, answer
            # E.g., "1. Aamkapo mtu hakosi kusema hivi: yuaa!- Kupiga miayo."
            match = re.match(r"^(\d+)\.\s*(.+?)\s*-\s*(.*)", line)
            
            if match:
                if current_entry:
                    entries.append(current_entry)
                
                current_entry = {
                    "number": int(match.group(1)),
                    "riddle": match.group(2).strip(),
                    "answer": match.group(3).strip(),
                    "explanation": "" # Some entries have explanations following
                }
            elif current_entry:
                # If it doesn't match the main pattern, it's likely an explanation for the previous riddle
                current_entry["explanation"] += " " + line
                
        if current_entry:
            entries.append(current_entry)
            
        return entries

    def save_to_json(self, output_path: str):
        entries = self.parse()
        for entry in entries:
            entry["riddle"] = re.sub(r"\s+", " ", entry["riddle"]).strip()
            entry["answer"] = re.sub(r"\s+", " ", entry["answer"]).strip()
            entry["explanation"] = re.sub(r"\s+", " ", entry["explanation"]).strip()
            
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
            
        print(f"🧩 Successfully parsed {len(entries)} Vitendawili (Riddles) entries into {output_path}!")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    raw_file = os.path.join(project_root, "data_inputs", "public_knowledge", "Vitendawilidoc.docx")
    output_file = os.path.join(project_root, "data_inputs", "public_knowledge", "vitendawili_clean.json")
    
    try:
        parser = VitendawiliParser(raw_file)
        parser.save_to_json(output_file)
    except Exception as e:
        print(f"Error: {e}")