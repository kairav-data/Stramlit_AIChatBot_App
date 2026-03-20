import os
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import io
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables. Assume .env.local is in the parent directory
load_dotenv("../.env.local")

# Get HF API Key
HF_API_KEY = os.getenv("VITE_HF_API_KEY")

if not HF_API_KEY:
    logger.warning("VITE_HF_API_KEY not found in environment variables. Inference will fail.")

# Initialize the Hugging Face Inference Client
try:
    client = InferenceClient(api_key=HF_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize InferenceClient: {e}")
    client = None


# Initialize FastAPI app
app = FastAPI(title="Lumina AI Backend")

# Initialize RAG components
vector_store = None
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Define CORS to allow requests from the React frontend running on Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://0.0.0.0:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class Message(BaseModel):
    role: str
    content: str
    id: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "Qwen/Qwen2.5-72B-Instruct"

# API Endpoints
@app.get("/api/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "Backend is running"}

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global vector_store
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        # Read PDF
        content = await file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
            
        # Chunk the text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)
        
        # Create FAISS vector store
        vector_store = FAISS.from_texts(chunks, embeddings)
        
        return {"status": "success", "message": f"Successfully processed {len(chunks)} chunks from the PDF."}
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/api/chat")
async def chat_completion(request: ChatRequest):
    """
    Handle chat completions by forwarding to Hugging Face Inference API.
    """
    if not client:
        raise HTTPException(status_code=500, detail="Hugging Face client is not initialized.")
    
    try:
        # Build messages for the API
        system_prompt = "You are a helpful, friendly website assistant. Keep responses concise and professional. Use markdown for formatting when appropriate."
        
        # Add RAG context if available
        if vector_store and request.messages:
            # Find the latest user message
            latest_user_msg = next((msg.content for msg in reversed(request.messages) if msg.role == "user"), None)
            
            if latest_user_msg:
                # Retrieve relevant chunks
                docs = vector_store.similarity_search(latest_user_msg, k=3)
                context = "\n\n".join([doc.page_content for doc in docs])
                
                if context:
                    system_prompt += f"\n\nUse the following context from an uploaded document to answer the user's question. If the answer is not in the context, use your general knowledge but mention that it's not in the document.\n\nContext:\n{context}"
        
        # Format conversation history
        api_messages = [{"role": "system", "content": system_prompt}]
        
        for msg in request.messages:
            # Hugging Face Chat API expects roles: 'system', 'user', or 'assistant'
            role = "assistant" if msg.role == "bot" else "user"
            content = msg.content.strip()
            
            if content: # don't send empty messages 
                api_messages.append({"role": role, "content": content})

        logger.info(f"Sending request to {request.model} with {len(api_messages)} messages.")

        # Let the inference client handle the chat flow
        response = client.chat_completion(
            model=request.model,
            messages=api_messages,
            max_tokens=500,
            temperature=0.7,
        )

        assistant_message = response.choices[0].message.content
        return {"response": assistant_message}

    except Exception as e:
        logger.error(f"Error during chat completion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")

# Add a simple root route for convenience
@app.get("/")
def read_root():
    return {"message": "Welcome to Lumina AI Backend API"}
