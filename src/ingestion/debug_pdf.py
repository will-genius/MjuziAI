import os
import PyPDF2

# Setup paths
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_script_dir))
pdf_path = os.path.join(project_root, "data_inputs", "public_knowledge", "kamusi_ya_tashbihi.pdf")

print(f"🔍 Reading: {pdf_path}\n")

try:
    import fitz  # PyMuPDF
    with fitz.open(pdf_path) as doc:
        # Read pages 1 and 2 (indexes 1 and 2) to bypass any blank covers
        text_page_1 = doc[1].get_text("text")
        text_page_2 = doc[2].get_text("text")
        
        raw_text = text_page_1 + "\n" + text_page_2
        
        print("--- START OF RAW PDF TEXT ---")
        print(raw_text[:1500])  # Print the first 1500 characters
        print("--- END OF RAW PDF TEXT ---")
except ImportError:
    print("❌ PyMuPDF is not installed. Run: pip install pymupdf")
except Exception as e:
    print(f"Error: {e}")