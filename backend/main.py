import os
import re
import numpy as np

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

chunks_store = []


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


def split_text(text: str, chunk_size: int = 1200, overlap: int = 200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def tokenize(text: str):
    return re.findall(r"\b\w+\b", text.lower())


def score_chunk(question: str, chunk: str) -> int:
    q_words = set(tokenize(question))
    c_words = set(tokenize(chunk))
    return len(q_words.intersection(c_words))


def retrieve_relevant_chunks(question: str, top_k: int = 3):
    global chunks_store

    if not chunks_store:
        return []

    scored = [(score_chunk(question, chunk), chunk) for chunk in chunks_store]
    scored.sort(key=lambda x: x[0], reverse=True)

    top_chunks = [chunk for score, chunk in scored[:top_k] if score > 0]

    if not top_chunks:
        top_chunks = chunks_store[:top_k]

    return top_chunks


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
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    return completion.choices[0].message.content


@app.get("/")
def home():
    return {"message": "PDF Assistant backend running"}


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    global chunks_store

    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Please upload a PDF file"}

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text_from_pdf(file_path)

    if not text.strip():
        return {"error": "No readable text found in PDF"}

    chunks_store = split_text(text)

    return {
        "message": "PDF uploaded and indexed successfully",
        "filename": file.filename,
        "chunks": len(chunks_store)
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