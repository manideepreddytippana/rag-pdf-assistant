import logging
from contextlib import asynccontextmanager
import uvicorn
import chromadb
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from schemas import UserRequest, ChatResponse
from services.pdf_reader import extract_pdf
from services.chunker import chunk_pages
from services.embeddings import EmbeddingService
from services.retriever import Retriever
from services.reranker import RerankerService
from services.llm import LLMService
from services.rag import RagService
from services.query_resolver import QueryResolver
from services.memory import Memory
from database import init_db

# Configure logging for the entire pipeline
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("rag_pipeline")

init_db()

class State:
    rag_service: RagService = None

state = State()

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    chroma_client = chromadb.PersistentClient(path=settings.chroma_db_dir)
    collection = chroma_client.get_or_create_collection(
        name='pdf_documents',
        metadata={"hnsw:space": "cosine"},
    )

    embedding_service = EmbeddingService()

    # Only process PDF if collection is empty — skip on subsequent restarts
    if collection.count() == 0:
        logger.info(f"ChromaDB empty — ingesting document from {settings.pdf_path}")

        document = extract_pdf(settings.pdf_path)
        pages = document['text_blocks']
        source = document['metadata']['source']
            
        chunks = chunk_pages(pages, source)
        chunks_embeddings = embedding_service.embed_documents(chunks)

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
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=chunks_embeddings,
        )
        logger.info(f"Ingested {len(chunks)} chunks into ChromaDB")
    else:
        logger.info(f"ChromaDB already has {collection.count()} documents, skipping ingestion")

    reranker_service = RerankerService()
    retriever = Retriever(collection, embedding_service, reranker_service=reranker_service)
    llm_service = LLMService()
    query_resolver = QueryResolver(llm_service)
    memory = Memory()

    state.rag_service = RagService(
        retriever=retriever,
        llmservice=llm_service,
        memory=memory,
        query_resolver=query_resolver
    )
    
    yield

app = FastAPI(title="RAG PDF Assistant API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
    allow_credentials=True
)

@app.get('/')
def home():
    return {'message': 'Welcome to RAG Application'}

@app.post('/chat', response_model=ChatResponse)
async def chat(request: UserRequest):
    '''Async endpoint that returns structured JSON for the frontend'''
    try:
        # Sanitize input — collapse excessive whitespace
        clean_query = " ".join(request.prompt.split())

        response = state.rag_service.get_answer(
            query=clean_query,
            session_id=request.session_id,
        )

        return {
            "answer": response["answer"],
            "sources": response["sources"],
            "question": response["question"]
        }

    except Exception as e:
        logger.error(f"Chat endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate response. Please try again.")

@app.get('/sessions')
async def list_sessions():
    '''List all active conversation sessions'''
    sessions = state.rag_service.memory.list_sessions()
    return {"sessions": sessions}

@app.delete('/sessions/{session_id}')
async def clear_session(session_id: str):
    '''Clear conversation history for a session'''
    cleared = state.rag_service.memory.clear_history(session_id)
    if cleared:
        return {"message": f"Session '{session_id}' history cleared"}
    return {"message": f"Session '{session_id}' not found"}

if __name__ == "__main__":
    uvicorn.run(app, port=settings.server_port)
