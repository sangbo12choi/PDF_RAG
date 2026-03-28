"""
프로젝트 설정 파일
"""
import os
from pathlib import Path

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent

# 경로 설정
VECTOR_CACHE_DIR = PROJECT_ROOT / "cache" / "chroma_pdf_cache"
PDF_DATA_DIR = PROJECT_ROOT / "data" / "pdfs"

# Ollama 모델 설정
OLLAMA_LLM_MODEL = "llama3"
OLLAMA_EMBEDDING_MODEL = "mxbai-embed-large"

# 텍스트 분할 설정
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# RAG 설정
TOP_K_RETRIEVAL = 4  # 검색할 문서 개수

# 시스템 프롬프트
SYSTEM_PROMPT = "You are a helpful assistant. Read the PDF content and answer the question. Translate the answer in Korean with emoji."

# 디렉토리 생성 (없으면)
VECTOR_CACHE_DIR.mkdir(parents=True, exist_ok=True)
PDF_DATA_DIR.mkdir(parents=True, exist_ok=True)

