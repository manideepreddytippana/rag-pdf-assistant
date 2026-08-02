import json

def chunk_text(text: str, chunk_size : int, overlap : int) -> list[str]:

    if chunk_size <=0 :
        raise ValueError("chunk_size value must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap cannot be negative value")
    
    chunks = []
    start = 0

    while start < len(text):

        end = start + chunk_size
        chunk = text[start: end].strip()

        if chunk:
            chunks.append(chunk)
        start +=  chunk_size - overlap

    return chunks

def chunk_pages(pages: list[dict], source: str, chunk_size: int= 600, overlap: int = 50) -> list[dict]:
    
    page_chunks = []
    chunk_id = 0
    
    for page in pages:
        chunks = chunk_text(text = page["text"], chunk_size = chunk_size, overlap = overlap)

        for chunk in chunks:
            page_chunks.append({
                "chunk_id": chunk_id,
                "source": "", # source not defined
                "page_no": page["page_no"],
                "text":chunk
            })
            chunk_id +=1
    return page_chunks