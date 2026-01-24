📄 AI Research Paper Tool
A full-stack web application that allows users to upload research paper PDFs and perform intelligent document analysis including metadata extraction, summarization, and PDF splitting.

Features :
📤 Upload PDF
📑 Extract Metadata (pages, title, author)
📝 Basic Text Summary
🤖 AI-based Summary (fast, lightweight extractive approach)
✂️ Split PDF by page number
🎨 Clean and modern React UI
⚙️ REST API powered by DjangO
semantic Search





🛠️ Tech Stack
Frontend
React.js
Axios
CSS (custom dashboard UI)
Backend
Django
Django REST Framework


🧠 AI Summary Approach
Instead of heavy transformer models, the system uses a lightweight extractive summarization technique:
Text extraction from PDF
Sentence ranking based on importance
Fast execution on CPU
Stable and suitable for local environments
This ensures speed, reliability, and low resource usage.
PyPDF2 (PDF processing)

