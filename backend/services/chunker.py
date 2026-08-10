from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings

def chunk_pages(
    pages: list[dict],
    source: str,
    chunk_size: int = None,
    overlap: int = None,
) -> list[dict]:

    target_chunk_size = chunk_size if chunk_size is not None else settings.chunk_size
    target_overlap = overlap if overlap is not None else settings.chunk_overlap

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=target_chunk_size,
        chunk_overlap=target_overlap,
        length_function=len,
        separators=[
            "\n\n\n",
            "\n\n",
            "\n",
            ". ",
            "; ",
            ", ",
            " ",
            "",
        ],
    )

    page_chunks = []
    chunk_id = 0

    for page in pages:
        chunks = splitter.split_text(page["text"])

        for chunk in chunks:
            page_chunks.append({
                "chunk_id": chunk_id,
                "source": source,
                "page_no": page["page_no"],
                "text": chunk,
            })
            chunk_id += 1

    return page_chunks