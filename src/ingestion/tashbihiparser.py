import os
import re
import json

class TashbihiParser:
    """
    Parser for the Tashbihi text you provided.
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
            if line_str and not line_str.startswith("Sehemu ya Kwanza:"):
                cleaned_lines.append(line_str)
        return cleaned_lines

    def parse(self) -> list[dict]:
        """Parses the text into structured tashbihi entries."""
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
        current_field = None
        
        for line in lines:
            # We look for lines starting with a number and a period or space, followed by text, or just text for the first few unnumbered ones
            num_match = re.match(r"^(\d+)\.\s*(.*)", line)
            
            if num_match:
                if current_entry:
                    entries.append(current_entry)
                
                num = int(num_match.group(1))
                phrase_start = num_match.group(2).strip()
                
                current_entry = {
                    "number": num,
                    "phrase": phrase_start,
                    "m.s.": "",
                    "m.y.": "",
                    "mf.": ""
                }
                current_field = "phrase"
                continue
            
            # Handle the first few entries that don't have numbers
            if not current_entry and not num_match and not re.match(r"^(m\.s\.|m\.y\.|mf:)", line, re.IGNORECASE):
                 current_entry = {
                    "number": len(entries) + 1,
                    "phrase": line.strip(),
                    "m.s.": "",
                    "m.y.": "",
                    "mf.": ""
                }
                 current_field = "phrase"
                 continue
                 
            ms_match = re.match(r"^(m\.s\.|M\.s\.)\s*(.*)", line)
            my_match = re.match(r"^(m\.y\.|M\.y\.)\s*(.*)", line)
            mf_match = re.match(r"^(mf:|mf\.)\s*(.*)", line, re.IGNORECASE)
            
            if ms_match:
                if current_entry:
                    current_entry["m.s."] = ms_match.group(2).strip()
                    current_field = "m.s."
                continue
            elif my_match:
                if current_entry:
                    current_entry["m.y."] = my_match.group(2).strip()
                    current_field = "m.y."
                continue
            elif mf_match:
                if current_entry:
                    current_entry["mf."] = mf_match.group(2).strip()
                    current_field = "mf."
                continue
            
            if current_entry and current_field:
                current_entry[current_field] += " " + line
                
        if current_entry:
            entries.append(current_entry)
            
        return entries

    def save_to_json(self, output_path: str):
        entries = self.parse()
        for entry in entries:
            entry["phrase"] = re.sub(r"\s+", " ", entry["phrase"]).strip()
            entry["m.s."] = re.sub(r"\s+", " ", entry["m.s."]).strip()
            entry["m.y."] = re.sub(r"\s+", " ", entry["m.y."]).strip()
            entry["mf."] = re.sub(r"\s+", " ", entry["mf."]).strip()
            
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
            
        print(f"🏆 Successfully parsed {len(entries)} Tashbihi entries into {output_path}!")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    raw_file = os.path.join(project_root, "data_inputs", "public_knowledge", "tashbihidoc.docx")
    output_file = os.path.join(project_root, "data_inputs", "public_knowledge", "tashbihi_clean.json")
    
    try:
        parser = TashbihiParser(raw_file)
        parser.save_to_json(output_file)
    except Exception as e:
        print(f"Error: {e}")