# RAG PDF Assistant

An intelligent PDF document analysis and conversational Q&A platform. RAG PDF Assistant ingests PDF documents, extracts text page-by-page, splits content into overlapping chunks, generates vector embeddings using `sentence-transformers`, stores them in ChromaDB, and provides an interactive RAG (Retrieval-Augmented Generation) chat interface powered by Hugging Face Inference API and the Qwen2.5-7B-Instruct model.

---

## 🚀 Features

- **PDF Text Extraction**:
  - Full-text extraction from multi-page PDF documents using `PyMuPDF` (`fitz`).
  - Captures rich document metadata (title, author, subject, keywords, creator, creation date, etc.).
- **Configurable Text Chunking**:
  - Character-level sliding-window chunking with adjustable `chunk_size` and `overlap` parameters.
  - Preserves page number mapping for accurate source citations.
- **Vector Search with ChromaDB**:
  - Generates normalized embeddings via `sentence-transformers` (`all-MiniLM-L6-v2`).
  - Persistent ChromaDB vector store with cosine similarity search (HNSW index).
  - Returns top-K relevant chunks with similarity scores, source file, and page numbers.
- **Advanced RAG Pipeline**:
  - **Query Decomposition**: Automatically splits complex multi-part questions into independent sub-queries for better retrieval coverage.
  - **Context-Aware Prompting**: Constructs grounded prompts from retrieved chunks with strict hallucination-prevention rules.
  - **Source Citations**: Every response includes source document name, page numbers, and relevance scores.
- **LLM Integration via Hugging Face**:
  - Uses Hugging Face Inference API with the `Qwen/Qwen2.5-7B-Instruct` model.
  - Configurable temperature and prompt templates (system prompt, prompt builder, and resume/analyzer prompt).
- **Modern Interactive Chat Frontend**:
  - Built with React 19, TypeScript, and Vite.
  - Real-time chat interface with typing indicators, auto-scroll, auto-resizing textarea, and keyboard shortcuts (Enter to send, Shift+Enter for newline).
  - Clean, responsive UI with user/assistant message bubbles and empty-state landing.

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 19 + TypeScript + Vite
- **HTTP Client**: Axios
- **Styling**: Vanilla CSS
- **Build Tool**: Vite 8

### Backend
- **Framework**: Python 3.10+ & FastAPI
- **PDF Extraction**: PyMuPDF (`fitz`)
- **Text Chunking**: Custom sliding-window chunker with overlap
- **Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Vector Store**: ChromaDB (persistent, cosine similarity, HNSW index)
- **LLM**: Hugging Face Inference API (`Qwen/Qwen2.5-7B-Instruct`)
- **Validation**: Pydantic v2
- **Utilities**: `python-dotenv`, `scikit-learn`, `numpy`

---

## ⚙️ Prerequisites

- **Node.js**: v18.0 or higher
- **Python**: v3.10 or higher
- **Hugging Face Account**: With an [API token](https://huggingface.co/settings/tokens) that has Inference API access

---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/manideepreddytippana/rag-pdf-assistant.git
cd rag-pdf-assistant
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:

```env
# Hugging Face API Token (required for LLM inference)
HF_TOKEN=your_huggingface_api_token

# Optional: Additional HF tokens for fallback/rotation
HF_TOKEN_2=your_secondary_hf_token
```

### 3. Backend Setup
Navigate to the `backend` directory and set up a virtual environment:

```bash
cd backend
python -m venv .venv

# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Frontend Setup
Open a new terminal and navigate to the `frontend` directory:

```bash
cd frontend
npm install
```

### 5. Add Your PDF Document
Place your PDF file in the `backend/data/` directory. Update the document path in `backend/main.py` if needed:

```python
DOCUMENTS_DIR = os.path.join(ROOT_DIR, "backend/data", "your_document.pdf")
```

---

## 🚀 Running the Application

### 1. Start the Backend Server
Ensure your virtual environment is active:

```bash
cd backend
uvicorn main:app --reload
```
- API Root: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. Start the Frontend Development Server
```bash
cd frontend
npm run dev
```
- Chat Interface: `http://localhost:5173`

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Service welcome / health check |
| `POST` | `/chat` | RAG-powered Q&A — send a prompt, receive an answer with source citations |

### Request Body (`POST /chat`)
```json
{
  "prompt": "What is the attention mechanism?"
}
```

### Response
```
The attention mechanism allows the model to focus on relevant parts of the input...

   source: attention.pdf , page : 3, source: attention.pdf , page : 5
```

---

## 🏗️ Architecture

```
User ──▶ React Chat UI ──▶ FastAPI /chat endpoint
                                │
                                ▼
                        Query Decomposer (LLM)
                        splits complex queries into sub-queries
                                │
                                ▼
                    ┌───────────────────────┐
                    │   For each sub-query  │
                    │                       │
                    │  1. Embed query        │
                    │  2. ChromaDB search    │
                    │  3. Build context      │
                    │  4. LLM generate       │
                    └───────────────────────┘
                                │
                                ▼
                        Merge answers + deduplicate sources
                                │
                                ▼
                        Return answer + citations
```

---

## 📂 Project Structure

```
rag-pdf-assistant/
├── backend/
│   ├── services/
│   │   ├── pdf_reader.py         # PDF text extraction & metadata parsing (PyMuPDF)
│   │   ├── chunker.py            # Sliding-window text chunking with overlap
│   │   ├── embeddings.py         # Sentence-transformer embedding service
│   │   ├── retriever.py          # ChromaDB vector similarity search
│   │   ├── query_decomposer.py   # LLM-powered multi-query decomposition
│   │   ├── rag.py                # RAG orchestration (context building, prompting, answer merging)
│   │   ├── llm.py                # Hugging Face Inference API client (Qwen2.5-7B)
│   │   └── prompts_retriever.py  # Prompt template file loader
│   ├── prompts/
│   │   ├── system_prompt.txt     # System prompt for RAG responses
│   │   ├── prompt_builder.txt    # Alternative prompt template
│   │   └── resume_prompt.txt     # Structured analysis prompt template
│   ├── data/                     # PDF documents for ingestion
│   ├── schemas.py                # Pydantic request/response schemas
│   ├── main.py                   # FastAPI entrypoint, lifespan setup, CORS, routes
│   └── requirements.txt          # Backend Python dependencies
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── api.ts            # Axios HTTP client (baseURL: localhost:8000)
│   │   ├── components/
│   │   │   ├── Chat.tsx          # Main chat component (messages, input, send logic)
│   │   │   └── Chat.css          # Chat UI styles
│   │   ├── App.tsx               # Root app component
│   │   ├── App.css               # App-level styles
│   │   ├── main.tsx              # React DOM entry point
│   │   └── index.css             # Global styles
│   ├── package.json              # Frontend dependencies & scripts
│   └── vite.config.ts            # Vite configuration
├── chroma_db/                    # Persistent ChromaDB vector store (auto-generated)
├── .env                          # Environment variables (HF tokens)
├── .gitignore                    # Git ignore rules
└── README.md
```

---

## 🔧 Configuration

### Chunking Parameters
Adjust in `backend/main.py`:
```python
chunks = chunk_pages(pages, source, chunk_size=600, overlap=50)
```
- `chunk_size`: Number of characters per chunk (default: 600)
- `overlap`: Character overlap between consecutive chunks (default: 50)

### LLM Settings
Configured in `backend/services/llm.py`:
- **Model**: `Qwen/Qwen2.5-7B-Instruct`
- **Temperature**: `0.2` (low for factual, grounded responses)

### Retrieval Settings
- **Top-K**: 5 (number of chunks retrieved per query, configurable in the `/chat` endpoint)
- **Similarity Metric**: Cosine (HNSW space in ChromaDB)


