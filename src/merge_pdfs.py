"""
PDF 파일들을 하나로 병합하는 스크립트
중복되는 내용은 제거하되, 누락되는 내용은 없도록 처리
"""
try:
    import fitz  # PyMuPDF
except ImportError:
    try:
        import pymupdf as fitz
    except ImportError:
        raise ImportError(
            "PyMuPDF가 설치되지 않았습니다. 'pip install PyMuPDF'를 실행하세요."
        )
from pathlib import Path
from typing import List, Set
import hashlib
from difflib import SequenceMatcher

# 설정 파일 import
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import PDF_DATA_DIR


def normalize_text(text: str) -> str:
    """텍스트를 정규화하여 비교하기 쉽게 만듦"""
    # 공백 제거 및 소문자 변환
    return ' '.join(text.lower().split())


def calculate_similarity(text1: str, text2: str) -> float:
    """두 텍스트의 유사도를 계산 (0.0 ~ 1.0)"""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    
    if not norm1 or not norm2:
        return 0.0
    
    return SequenceMatcher(None, norm1, norm2).ratio()


def get_page_hash(page) -> str:
    """페이지의 텍스트 해시를 생성"""
    text = page.get_text()
    normalized = normalize_text(text)
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()


def is_duplicate_page(page, existing_pages: List[dict], similarity_threshold: float = 0.85) -> bool:
    """
    페이지가 기존 페이지와 중복인지 확인
    similarity_threshold: 유사도 임계값 (0.85 = 85% 이상 유사하면 중복으로 간주)
    """
    page_text = page.get_text()
    page_hash = get_page_hash(page)
    
    # 해시가 같으면 완전 중복
    for existing in existing_pages:
        if existing['hash'] == page_hash:
            return True
    
    # 텍스트 유사도로 확인 (짧은 텍스트는 제외)
    if len(normalize_text(page_text)) < 50:  # 너무 짧은 페이지는 유사도 체크 스킵
        return False
    
    for existing in existing_pages:
        similarity = calculate_similarity(page_text, existing['text'])
        if similarity >= similarity_threshold:
            return True
    
    return False


def merge_pdfs(
    input_dir: Path = PDF_DATA_DIR,
    output_path: Path = None,
    similarity_threshold: float = 0.85,
    preserve_order: bool = True
) -> Path:
    """
    PDF 파일들을 하나로 병합
    
    Args:
        input_dir: 입력 PDF 파일들이 있는 디렉토리
        output_path: 출력 PDF 파일 경로 (None이면 자동 생성)
        similarity_threshold: 중복 판단 유사도 임계값 (0.0 ~ 1.0)
        preserve_order: 파일명 순서대로 병합할지 여부
    
    Returns:
        생성된 PDF 파일 경로
    """
    if output_path is None:
        output_path = input_dir.parent / "merged_pdf.pdf"
    
    # PDF 파일 목록 가져오기
    pdf_files = sorted([f for f in input_dir.glob("*.pdf") if f.is_file()])
    
    if not pdf_files:
        raise ValueError(f"[오류] {input_dir}에 PDF 파일이 없습니다.")
    
    print(f"[정보] 총 {len(pdf_files)}개의 PDF 파일을 찾았습니다:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf_file.name}")
    
    # 새 PDF 문서 생성
    merged_doc = fitz.open()
    existing_pages: List[dict] = []  # 중복 체크를 위한 기존 페이지 정보
    total_pages = 0
    added_pages = 0
    skipped_pages = 0
    
    print(f"\n[진행] PDF 병합 시작...")
    print(f"   중복 판단 임계값: {similarity_threshold * 100:.0f}%")
    
    # 각 PDF 파일 처리
    for pdf_file in pdf_files:
        print(f"\n[처리] {pdf_file.name}")
        try:
            doc = fitz.open(str(pdf_file))
            file_pages = 0
            file_added = 0
            file_skipped = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                total_pages += 1
                file_pages += 1
                
                # 중복 체크
                if is_duplicate_page(page, existing_pages, similarity_threshold):
                    skipped_pages += 1
                    file_skipped += 1
                    print(f"   [건너뜀] 페이지 {page_num + 1}: 중복으로 건너뜀")
                    continue
                
                # 새 페이지 추가
                merged_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                added_pages += 1
                file_added += 1
                
                # 기존 페이지 목록에 추가
                page_text = page.get_text()
                existing_pages.append({
                    'hash': get_page_hash(page),
                    'text': page_text
                })
            
            print(f"   [완료] {file_pages}페이지 중 {file_added}페이지 추가, {file_skipped}페이지 건너뜀")
            doc.close()
            
        except Exception as e:
            print(f"   [오류] {str(e)}")
            continue
    
    # 결과 저장
    if added_pages == 0:
        raise ValueError("[오류] 병합할 페이지가 없습니다.")
    
    merged_doc.save(str(output_path))
    merged_doc.close()
    
    print(f"\n[완료] PDF 병합 완료!")
    print(f"   [통계]")
    print(f"      - 총 페이지: {total_pages}")
    print(f"      - 추가된 페이지: {added_pages}")
    print(f"      - 건너뛴 페이지 (중복): {skipped_pages}")
    print(f"      - 출력 파일: {output_path}")
    
    return output_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PDF 파일들을 하나로 병합")
    parser.add_argument(
        "--input-dir",
        type=str,
        default=None,
        help="입력 PDF 파일 디렉토리 (기본값: data/pdfs)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="출력 PDF 파일 경로 (기본값: data/merged_pdf.pdf)"
    )
    parser.add_argument(
        "--similarity",
        type=float,
        default=0.85,
        help="중복 판단 유사도 임계값 (0.0 ~ 1.0, 기본값: 0.85)"
    )
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir) if args.input_dir else PDF_DATA_DIR
    output_path = Path(args.output) if args.output else None
    
    try:
        result_path = merge_pdfs(
            input_dir=input_dir,
            output_path=output_path,
            similarity_threshold=args.similarity
        )
        print(f"\n[성공] 병합된 PDF: {result_path}")
    except Exception as e:
        print(f"\n[오류] {str(e)}")
        exit(1)

