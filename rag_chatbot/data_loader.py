import json
from langchain.schema import Document

def clean_details(details_raw):
    if details_raw.startswith("```json"):
        details_raw = details_raw.replace("```json", "").replace("```", "").strip()
    return details_raw

def load_json_documents(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    docs = []
    for entry in data:
        source = entry["image"]
        raw_text = clean_details(entry["details"])
        docs.append(Document(page_content=raw_text, metadata={"source": source}))
    
    return docs
