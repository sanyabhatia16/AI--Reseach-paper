from django.urls import path
from .views import (
    upload_pdf,
    extract_metadata,
    basic_summary,
    ai_summary,
    split_pdf,
    semantic_search,
    build_faiss_index,
    method1,
)

urlpatterns = [
    path("upload/", upload_pdf),
    path("metadata/", extract_metadata),
    path("summary/", basic_summary),
    path("ai-summary/", ai_summary),
    path("split/", split_pdf),
    path("index-pdf/", build_faiss_index),
    path("semantic-search/", semantic_search),
    path("test-llm/", method1),
]
