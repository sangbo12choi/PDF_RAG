# PDF RAG 프로젝트

PDF 문서를 기반으로 한 RAG(Retrieval-Augmented Generation) 시스템입니다. Ollama를 사용하여 로컬에서 실행되며, 한국어로 질문에 답변합니다.

## 📁 프로젝트 구조

```
PDF_RAG/
├── main.py                 # 메인 실행 파일
├── requirements.txt        # Python 의존성
├── README.md              # 프로젝트 설명서
├── .gitignore            # Git 무시 파일
│
├── src/                   # 소스 코드
│   ├── __init__.py
│   └── Ollama_PDF_RAG.py  # 메인 RAG 로직
│
├── config/                # 설정 파일
│   ├── __init__.py
│   └── settings.py        # 프로젝트 설정
│
├── data/                  # 데이터 파일
│   └── pdfs/             # PDF 파일 저장소
│
├── cache/                 # 캐시 파일
│   └── chroma_pdf_cache/ # 벡터 데이터베이스 캐시
│
└── tests/                 # 테스트 파일 (향후 추가)
```

## 🚀 시작하기

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. Ollama 설치 및 모델 다운로드

Ollama가 설치되어 있어야 합니다. [Ollama 공식 사이트](https://ollama.ai/)에서 설치하세요.

필요한 모델 다운로드:
```bash
ollama pull llama3
ollama pull mxbai-embed-large
```

### 3. 실행

```bash
python main.py
```

Gradio 웹 인터페이스가 자동으로 열립니다.

## ⚙️ 설정

`config/settings.py` 파일에서 다음 설정을 변경할 수 있습니다:

- **OLLAMA_LLM_MODEL**: LLM 모델명 (기본값: `llama3`)
- **OLLAMA_EMBEDDING_MODEL**: 임베딩 모델명 (기본값: `mxbai-embed-large`)
- **CHUNK_SIZE**: 텍스트 분할 크기 (기본값: `1000`)
- **CHUNK_OVERLAP**: 텍스트 분할 오버랩 (기본값: `200`)
- **TOP_K_RETRIEVAL**: 검색할 문서 개수 (기본값: `4`)

## ✨ 주요 기능

- 📄 **PDF 문서 업로드**: PDF 파일을 업로드하여 질문에 답변
- 🔍 **벡터 검색**: 의미 기반 문서 검색
- 💾 **캐시 시스템**: 파일 해시 기반 벡터 저장소 캐싱
- 🇰🇷 **한국어 지원**: 한국어로 질문하고 답변받기
- 🖥️ **웹 인터페이스**: Gradio 기반 사용자 친화적 UI

## 🔧 기술 스택

- **Ollama**: 로컬 LLM 실행
- **LangChain**: RAG 파이프라인 구축
- **ChromaDB**: 벡터 데이터베이스
- **Gradio**: 웹 UI 프레임워크
- **PyMuPDF**: PDF 처리

## 📝 사용 방법

1. 웹 인터페이스에서 PDF 파일을 업로드합니다.
2. 질문을 입력합니다.
3. 시스템이 PDF 내용을 기반으로 답변을 생성합니다.

**참고**: 첫 번째 업로드 시 벡터화 과정이 시간이 걸릴 수 있습니다. 이후 같은 파일을 업로드하면 캐시를 사용하여 빠르게 처리됩니다.

## 🐛 문제 해결

### Ollama 연결 오류
- Ollama 서비스가 실행 중인지 확인하세요: `ollama list`
- 모델이 다운로드되었는지 확인하세요: `ollama list`

### 메모리 부족
- `CHUNK_SIZE`를 줄이거나 더 작은 PDF 파일을 사용하세요.

## 📄 라이선스

이 프로젝트는 개인 사용 목적으로 제작되었습니다.
