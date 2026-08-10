import pymupdf
import os

def extract_pdf(file_path: str):

    document = pymupdf.open(file_path)
    doc_name = os.path.basename(file_path)
    metadata = {
        "title": document.metadata.get("title"),
        "author": document.metadata.get("author"),
        "subject": document.metadata.get("subject"),
        "keywords": document.metadata.get("keywords"),
        "creator": document.metadata.get("creator"),
        "producer": document.metadata.get("producer"),
        "creation_date": document.metadata.get("creation_date"),
        "mod_date": document.metadata.get("mod_date"),
        "source": doc_name
    }

    text_blocks = []
    for i, page in enumerate(document):
        text_blocks.append({
            "text": page.get_text(),
            "page_no": i + 1
        })

    result = {
        "text_blocks": text_blocks,
        "total_pages": len(document),
        "metadata": metadata
    }
    return result
