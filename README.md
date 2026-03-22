# 📄 AI PDF Assistant

An AI-powered web application that allows users to upload PDF documents and ask questions based on their content.

---

## 🚀 Features

* 📤 Upload PDF files
* 📖 Extract and process document text
* 🤖 Ask questions from PDF content
* ⚡ Fast responses using LLM (Groq - LLaMA)
* 🌐 Fully deployed (Frontend + Backend)

---

## 🧠 Tech Stack

### Frontend

* HTML, CSS, JavaScript
* Hosted on **Vercel**

### Backend

* FastAPI (Python)
* Hosted on **Railway**

### AI / LLM

* Groq API (LLaMA 3)

---

## ⚙️ How It Works

1. User uploads a PDF
2. Backend extracts text using PyPDF
3. Text is split into chunks
4. Relevant chunks are selected based on question
5. LLM generates answer using context

---

## 🌐 Live Demo

👉 Frontend:
https://pdf-ai-assistant-delta.vercel.app

👉 Backend API:
https://pdf-ai-assistant-production.up.railway.app/docs

---

## 📂 Project Structure

```
pdf-assistant/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│
├── uploads/
├── Dockerfile
├── .dockerignore
├── railway.json
└── README.md
```

---

## 🛠️ Setup (Local)

```bash
# Clone repo
git clone <https://github.com/geetikatoppo/pdf-ai-assistant.git>

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
Open index.html in browser
```

---

## 📌 Future Improvements

* Chat history support
* Better UI (ChatGPT-like)
* Semantic search with embeddings
* Multi-PDF support

---

##  Resume Highlight

> Built an AI-powered PDF Assistant using FastAPI and JavaScript, enabling document upload, context retrieval, and question answering. Deployed backend on Railway and frontend on Vercel.

---

## Author

**Geetika Toppo**
