import os
import json
from contextlib import asynccontextmanager

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from huggingface_hub import InferenceClient

from schemas import UserRequest, ModelResponse
from services.pdf_reader import extract_pdf
from services.chunker import chunk_pages
from services.embeddings import EmbeddingService
from services.retriever import Retriever
from services.llm import LLMService
from services.rag import RagService
from services.prompts_retriever import get_prompt

load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN_2')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DOCUMENTS_DIR = os.path.join(ROOT_DIR, "backend/data", "attention.pdf")
CHROMA_DB_DIR = os.path.join(ROOT_DIR, 'chroma_db')

class State:
    rag_service: RagService = None
    hf_client: InferenceClient = None

state = State()

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    document = extract_pdf(DOCUMENTS_DIR)
    pages = document['text_blocks']
    source = document['metadata']['source']
    
    chunks = chunk_pages(pages, source, chunk_size = 600, overlap = 50)
    
    embedding_service = EmbeddingService()
    chunks_embeddings = embedding_service.embed_documents(chunks)
    
    chroma_client = chromadb.PersistentClient(path = CHROMA_DB_DIR)
    collection = chroma_client.get_or_create_collection(
        name = 'pdf_documents',
        metadata = {"hnsw:space": "cosine"},
    )

    if collection.count() == 0:
        print("Populating chromadb with document chunks")
    
        ids = [str(chunk["chunk_id"]) for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [
            {
                "source": chunk['source'] if chunk['source'] else "unknown",
                "chunk_id": str(chunk['chunk_id']),
                "page_no": chunk["page_no"]
            } for chunk in chunks
        ]
    
        collection.add(
            ids = ids,
            documents = documents,
            metadatas = metadatas,
            embeddings = chunks_embeddings,
        )
       
    retriever = Retriever( collection, embedding_service)
    llm_service = LLMService()

    state.rag_service = RagService(retriever, llm_service)
    state.hf_client = InferenceClient(provider='auto', token=HF_TOKEN)
    
    yield

app = FastAPI(lifespan = lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173"],
    allow_methods = ["*"],
    allow_headers = ["*"],
    allow_credentials = True
)

@app.get('/')
def home():
    return {'message': 'Welcome to RAG Application'}

@app.post('/chat')
def chat(request : UserRequest):
    '''function to answer user question using RAG'''
    response = state.rag_service.get_answer(
            query=request.prompt,
            top_k=5,
        )   

    print("RETRIEVER RESULTS:")
    print(response)

    try:
        source = ', '.join(
            f"source: {source['source']} , page : {source['page_no']}"
            for source in response['sources']
        )
        return f"{response['answer']} \n\n   {source}"
    except json.JSONDecodeError:
        return {'message': 'Error parsing the model output'}


