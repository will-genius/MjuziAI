import os
import re
import json
import PyPDF2
from langchain_core.documents import Document

class BaseCulturalParser:
    """
    Base parser providing shared PDF text layer extraction and common 
    OCR cleaning utilities for the MjuziAI cultural and bilingual pipeline.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_text_from_pdf(self) -> str:
        """Extracts text layer from a PDF file using PyPDF2."""
        text_content = []
        try:
            with open(self.file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            return "\n".join(text_content)
        except Exception as e:
            raise RuntimeError(f"❌ Failed to extract PDF text: {e}")

    def clean_lines(self, raw_text: str, ignore_patterns: list[str] = None) -> list[str]:
        lines = raw_text.split("\n")
        cleaned = []
        base_ignore = [
            r"^\[Page \d+\]",
            r"^\d+$",
            r"^\s*$",
            r"KENYA NATIONAL LIBRARY SERVICE",
            r"KIMATHI UNIVERSITY LIBRARY",
            r"Sehemu ya.*"
        ]
        if ignore_patterns:
            base_ignore.extend(ignore_patterns)

        for line in lines:
            line_str = line.strip()
            if any(re.match(pattern, line_str, re.IGNORECASE) for pattern in base_ignore):
                continue
            cleaned.append(line_str)
        return cleaned

class MethaliParser(BaseCulturalParser):
    def parse(self) -> list[dict]:
        lines = self.clean_lines(self.extract_text_from_pdf(), [r"^Sehemu ya Pili", r"^Kamusi ya Methali"])
        entries = []
        current_entry = None
        current_field = None
        for line in lines:
            num_match = re.match(r"^(\d+)\s+(.*)", line)
            if num_match:
                if current_entry: entries.append(current_entry)
                current_entry = {"number": int(num_match.group(1)), "proverb": num_match.group(2).strip(), "m.s.": "", "m.y.": "", "mat.": ""}
                current_field = "proverb"
                continue
            ms_match = re.search(r"^(m\.?s\.?)\s*(.*)", line, re.IGNORECASE)
            my_match = re.search(r"^(m\.?y\.?)\s*(.*)", line, re.IGNORECASE)
            mat_match = re.search(r"^(mat\.?|matumizi:?)\s*(.*)", line, re.IGNORECASE)
            if ms_match: 
                if current_entry: current_entry["m.s."] = ms_match.group(2).strip(); current_field = "m.s."
            elif my_match: 
                if current_entry: current_entry["m.y."] = my_match.group(2).strip(); current_field = "m.y."
            elif mat_match: 
                if current_entry: current_entry["mat."] = mat_match.group(2).strip(); current_field = "mat."
            elif current_entry and current_field:
                current_entry[current_field] += " " + line
        if current_entry: entries.append(current_entry)
        return entries

class TashbihiParser(BaseCulturalParser):
    def parse(self) -> list[dict]:
        lines = self.clean_lines(self.extract_text_from_pdf(), [r"^Sehemu ya Kwanza: Tashbihi"])
        entries = []
        current_entry = None
        current_field = None
        for line in lines:
            num_match = re.match(r"^(\d+)\.?\s*(.*)", line)
            if num_match:
                if current_entry: entries.append(current_entry)
                current_entry = {"number": int(num_match.group(1)), "phrase": num_match.group(2).strip(), "m.y.": "", "mf": ""}
                current_field = "phrase"
                continue
            my_match = re.search(r"^(m\.?y\.?|m\.?s\.?)\s*(.*)", line, re.IGNORECASE)
            mf_match = re.search(r"^(mf\.?:?)\s*(.*)", line, re.IGNORECASE)
            if my_match:
                if current_entry: current_entry["m.y."] = my_match.group(2).strip(); current_field = "m.y."
            elif mf_match:
                if current_entry: current_entry["mf"] = mf_match.group(2).strip(); current_field = "mf"
            elif current_entry and current_field:
                current_entry[current_field] += " " + line
        if current_entry: entries.append(current_entry)
        return entries

if __name__ == "__main__":
    data_dir = os.path.join("data_inputs", "public_knowledge")
    tasks = [
        ("kamusi_ya_tashbihi.pdf", TashbihiParser, "clean_tashbihi.json"),
        ("Kamusi ya methali.pdf", MethaliParser, "clean_methali.json")
    ]
    for name, Parser, out in tasks:
        path = os.path.join(data_dir, name)
        if os.path.exists(path):
            data = Parser(path).parse()
            with open(os.path.join(data_dir, out), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)