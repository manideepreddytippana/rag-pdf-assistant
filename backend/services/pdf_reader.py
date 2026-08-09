import pymupdf
import os
import json

def extract_pdf(file_path : str):
    
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




















    

# document = read_pdf(DOCUMENTS_DIR)

# doc_path = document.name
# doc_name = os.path.basename(doc_path)

# no_of_pages = len(document)


# content = {
#     "text_blocks": [],
#     "total_pages": no_of_pages,
#     "metadata": metadata
# }
# text_content = ""
# for i, page in enumerate(document):

#     text_content += page.get_text()
#     json_content = content["text_blocks"].append({
#         "text": page.get_text(),
#         "page": i+1,
#         "page_font":document.get_page_fonts(i)
#     })
#     # print(f"Page {i}:")
#     # print(page.get_text())

# with open(f'{JSON_DIR}/jdd.json', 'w') as f:
#     json.dump(content, f)


# with open(f"{TEXT_DIR}/ssd.txt",'w', encoding="utf-8") as f:
#     f.write(text_content)

# doc_path = document.name
# doc_name = os.path.basename(doc_path)

# # with open(f"{doc_name}.txt","w") as f:
# #     f.write(text_)

# # print("------------------"*10)
# # print(text_content)
# # print(doc_name)
# # print(document.get_page_fonts())



