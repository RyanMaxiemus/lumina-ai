"""RAG Document Parser Utilities"""
import os
import fitz  # PyMuPDF

def parse_document(file_path: str) -> str:
    """Parse a document and extract its text content.
    
    Supports .txt, .md, .csv, and .pdf.
    """
    if not os.path.exists(file_path):
        return ""
        
    ext = os.path.splitext(file_path)[1].lower()
    content = ""
    
    try:
        if ext in ['.txt', '.md', '.csv']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        elif ext == '.pdf':
            with fitz.open(file_path) as doc:
                for page in doc:
                    content += page.get_text()
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
    except Exception as e:
        print(f"Error parsing document {file_path}: {e}")
        
    return content
