# Ollama_PDF_RAG.py
import gradio as gr
import ollama
import os
import hashlib
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

# 설정 파일 import
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import (
    VECTOR_CACHE_DIR,
    OLLAMA_LLM_MODEL,
    OLLAMA_EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K_RETRIEVAL,
    SYSTEM_PROMPT
)

# 파일 해시 생성 (캐시 키로 사용)
def get_file_hash(file_path: str) -> str:
    """파일의 해시값을 생성하여 캐시 키로 사용"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# PDF 문서 로드 및 벡터화
def load_and_retrieve_pdf(file_path: str):
    """PDF를 로드하고 벡터화하여 검색기 반환 (캐시 활용)"""
    file_path = Path(file_path)
    
    # 파일 해시로 캐시 확인
    file_hash = get_file_hash(str(file_path))
    cache_path = Path(VECTOR_CACHE_DIR) / file_hash
    
    # 캐시가 존재하면 재사용
    if cache_path.exists() and any(cache_path.iterdir()):
        print(f"✅ 캐시된 벡터 저장소를 사용합니다: {file_hash[:8]}...")
        embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
        vectorstore = Chroma(
            persist_directory=str(cache_path),
            embedding_function=embeddings
        )
        return vectorstore.as_retriever(search_kwargs={"k": TOP_K_RETRIEVAL})
    
    # 캐시가 없으면 새로 생성
    print(f"📄 PDF 문서 로드 중: {file_path.name}")
    loader = PyMuPDFLoader(str(file_path))
    docs = loader.load()

    if not docs:
        raise ValueError("❗ PDF에서 텍스트를 추출할 수 없습니다. 다른 파일을 시도해 보세요.")

    print(f"✅ PDF 문서 로드 완료. 첫 페이지 미리보기:\n{docs[0].page_content[:300]}...\n")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, 
        chunk_overlap=CHUNK_OVERLAP
    )
    splits = text_splitter.split_documents(docs)
    print(f"📝 텍스트를 {len(splits)}개의 청크로 분할했습니다.")
    
    embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
    print(f"🔄 벡터 임베딩 생성 중... (모델: {OLLAMA_EMBEDDING_MODEL})")

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=str(cache_path)
    )
    vectorstore.persist()
    print(f"💾 벡터 저장소를 캐시에 저장했습니다: {file_hash[:8]}...")

    return vectorstore.as_retriever(search_kwargs={"k": TOP_K_RETRIEVAL})

# 문서 포맷팅
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# RAG 체인 동작
def rag_chain(file, question: str) -> str:
    try:
        retriever = load_and_retrieve_pdf(file.name)
        retrieved_docs = retriever.invoke(question)

        if not retrieved_docs:
            return "관련 문서를 찾을 수 없습니다. 질문을 더 구체적으로 작성해 보거나 다른 PDF를 사용해 보세요."

        context = format_docs(retrieved_docs)
        print(f"검색된 문맥 미리보기:\n{context[:500]}...\n")

        prompt = f"Question: {question}\n\nContext: {context}"

        print(f"🤖 LLM으로 답변 생성 중... (모델: {OLLAMA_LLM_MODEL})")
        response = ollama.chat(
            model=OLLAMA_LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response['message']['content']

    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"

# Gradio 인터페이스
iface = gr.Interface(
    fn=rag_chain,
    inputs=[
        gr.File(label="PDF 파일 업로드", type="filepath"),
        gr.Textbox(label="질문을 입력하세요")
    ],
    outputs="text",
    title="LLaMA 3 - PDF 기반 질문 응답 (개선 버전)",
    description="PDF 파일을 올리고 질문을 입력하면, 해당 내용을 기반으로 LLaMA 3가 한국어로 답변해 줍니다."
)

if __name__ == "__main__":
    iface.launch()
