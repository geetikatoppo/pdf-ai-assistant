import os
import numpy as np
import faiss

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory storage for MVP
chunks_store = []
faiss_index = None

# Embedding model
embed_model = None

def get_embed_model():
    global embed_model
    if embed_model is None:
        embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    return embed_model


class QueryRequest(BaseModel):
    question: str


def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def split_text(text: str, chunk_size: int = 500, overlap: int = 100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def build_faiss_index(chunks):
    global faiss_index, chunks_store

    chunks_store = chunks
    embeddings = embed_model.encode(chunks, convert_to_numpy=True)

    dimension = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(embeddings.astype("float32"))


def retrieve_relevant_chunks(question: str, top_k: int = 3):
    global faiss_index, chunks_store

    if faiss_index is None or not chunks_store:
        return []

    query_embedding = embed_model.encode([question], convert_to_numpy=True).astype("float32")
    distances, indices = faiss_index.search(query_embedding, top_k)

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(chunks_store):
            results.append(chunks_store[idx])
    return results


def ask_llama(question: str, context_chunks):
    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a helpful PDF research assistant.
Answer only from the provided document context.
If the answer is not in the context, say: "I could not find that in the document."

Document context:
{context}

Question:
{question}

Answer in simple clear language.
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    return completion.choices[0].message.content


@app.get("/")
def home():
    return {"message": "PDF Assistant backend running"}


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Please upload a PDF file"}

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text_from_pdf(file_path)

    if not text.strip():
        return {"error": "No readable text found in PDF"}

    chunks = split_text(text)
    build_faiss_index(chunks)

    return {
        "message": "PDF uploaded and indexed successfully",
        "filename": file.filename,
        "chunks": len(chunks)
    }


@app.post("/ask")
def ask_question(data: QueryRequest):
    relevant_chunks = retrieve_relevant_chunks(data.question, top_k=3)

    if not relevant_chunks:
        return {"answer": "No document indexed yet. Please upload a PDF first."}

    answer = ask_llama(data.question, relevant_chunks)

    return {
        "answer": answer,
        "context_used": relevant_chunks
    }