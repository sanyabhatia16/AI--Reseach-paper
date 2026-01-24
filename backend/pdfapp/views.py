import os
from pathlib import Path
from dotenv import load_dotenv

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from django.core.files.storage import default_storage

from PyPDF2 import PdfReader, PdfWriter

import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from transformers import pipeline

from langchain_groq import ChatGroq


# =====================================================
# ENV
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# =====================================================
# GROQ LLM (STABLE MODEL)
# =====================================================

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0.2
)


# =====================================================
# GLOBAL MODELS
# =====================================================

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

faiss_index = None
stored_chunks = []

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)


# =====================================================
# HELPERS
# =====================================================

def read_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def chunk_text(text, size=500):
    return [text[i:i + size] for i in range(0, len(text), size)]


# =====================================================
# 1️⃣ UPLOAD PDF
# =====================================================

@api_view(["POST"])
def upload_pdf(request):
    if "file" not in request.FILES:
        return Response({"error": "No file uploaded"}, status=400)

    file = request.FILES["file"]
    filename = default_storage.save(file.name, file)

    return Response({"filename": filename})


# =====================================================
# 2️⃣ METADATA
# =====================================================

@api_view(["POST"])
def extract_metadata(request):
    filename = request.data.get("filename")

    if not filename:
        return Response({"error": "filename required"}, status=400)

    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    reader = PdfReader(file_path)

    meta = reader.metadata or {}

    return Response({
        "pages": len(reader.pages),
        "title": meta.get("/Title"),
        "author": meta.get("/Author"),
    })


# =====================================================
# 3️⃣ BASIC SUMMARY
# =====================================================

@api_view(["POST"])
def basic_summary(request):
    filename = request.data.get("filename")

    if not filename:
        return Response({"summary": ""})

    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    text = read_pdf(file_path)

    summary = " ".join(text.split()[:150])

    return Response({"summary": summary})


# =====================================================
# 4️⃣ AI SUMMARY (GROQ SAFE)
# =====================================================

@api_view(["POST"])
def ai_summary(request):
    try:
        filename = request.data.get("filename")

        if not filename:
            return Response({"error": "filename missing"}, status=400)

        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        text = read_pdf(file_path)

        if not text.strip():
            return Response({"ai_summary": "No readable text found"})

        text = text[:3500]  # prevent token overflow

        response = llm.invoke(
            f"Summarize this document clearly:\n{text}"
        )

        return Response({"ai_summary": response.content})

    except Exception as e:
        print("AI SUMMARY ERROR:", e)
        return Response({"error": str(e)}, status=500)


# =====================================================
# 5️⃣ SPLIT PDF
# =====================================================

@api_view(["POST"])
def split_pdf(request):
    filename = request.data.get("filename")
    page = request.data.get("page")

    if not filename or page is None:
        return Response({"error": "filename and page required"}, status=400)

    page = int(page)
    file_path = os.path.join(settings.MEDIA_ROOT, filename)

    reader = PdfReader(file_path)
    w1, w2 = PdfWriter(), PdfWriter()

    for i, p in enumerate(reader.pages):
        if i < page:
            w1.add_page(p)
        else:
            w2.add_page(p)

    part1 = f"part1_{filename}"
    part2 = f"part2_{filename}"

    with open(os.path.join(settings.MEDIA_ROOT, part1), "wb") as f:
        w1.write(f)

    with open(os.path.join(settings.MEDIA_ROOT, part2), "wb") as f:
        w2.write(f)

    return Response({
        "file_part_1": part1,
        "file_part_2": part2
    })


# =====================================================
# 6️⃣ BUILD FAISS INDEX
# =====================================================

@api_view(["POST"])
def build_faiss_index(request):
    global faiss_index, stored_chunks

    filename = request.data.get("filename")

    if not filename:
        return Response({"error": "filename required"}, status=400)

    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    text = read_pdf(file_path)

    chunks = chunk_text(text)

    embeddings = embedding_model.encode(chunks)

    faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
    faiss_index.add(np.array(embeddings))

    stored_chunks = chunks

    return Response({
        "message": "FAISS index built successfully",
        "total_chunks": len(chunks)
    })


# =====================================================
# 7️⃣ SEMANTICf faiss_index is None: SEARCH
# =====================================================

@api_view(["POST"])
def semantic_search(request):
    print("REQUEST DATA:", request.data)

    query = request.data.get("query")

    if not query:
        return Response(
            {
                "error": "query missing",
                "received": request.data
            },
            status=400
        )

    if faiss_index is None:
        return Response(
            {"error": "FAISS index not built"},
            status=400
        )

    query_embedding = embedding_model.encode([query])
    distances, indices = faiss_index.search(query_embedding, k=3)

    results = [stored_chunks[i] for i in indices[0]]

    return Response({
        "query": query,
        "results": results
    })


# =====================================================
# 8️⃣ LLM TEST
# =====================================================

@api_view(["GET"])
def method1(request):
    response = llm.invoke("What is an API?")
    return Response({"llm_response": response.content})
