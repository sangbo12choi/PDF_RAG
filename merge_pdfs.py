"""
PDF 병합 스크립트 실행 파일
"""
from src.merge_pdfs import merge_pdfs
from pathlib import Path
from config.settings import PDF_DATA_DIR

if __name__ == "__main__":
    try:
        output_path = PDF_DATA_DIR.parent / "merged_pdf.pdf"
        result_path = merge_pdfs(
            input_dir=PDF_DATA_DIR,
            output_path=output_path,
            similarity_threshold=0.85  # 85% 이상 유사하면 중복으로 간주
        )
        print(f"\n[성공] 병합된 PDF: {result_path}")
    except Exception as e:
        print(f"\n[오류] {str(e)}")
        exit(1)

