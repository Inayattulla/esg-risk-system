import sys
import os
import fitz  # PyMuPDF
import traceback

def extract_text_from_pdf(pdf_path):
    try:
        if not os.path.exists(pdf_path):
            print(f"[ERROR] File not found: {pdf_path}")
            return

        doc = fitz.open(pdf_path)
        print(f"[INFO] Opened {pdf_path} with {len(doc)} pages")

        full_text = ""
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            full_text += text + "\n"
            print(f"[INFO] Page {page_num}: {'Text found' if text.strip() else 'No text found'}")

        doc.close()

        if not full_text.strip():
            print("[WARNING] No extractable text found in the PDF.")
            return

        with open("extracted_text.txt", "w", encoding="utf-8") as f:
            f.write(full_text)

        print("[SUCCESS] extracted_text.txt successfully created")

    except Exception as e:
        print("[EXCEPTION] Error in extract_text.py:")
        traceback.print_exc()

# CLI usage
if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            raise ValueError("PDF path not provided to extract_text.py")

        pdf_path = sys.argv[1]
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"[ERROR] File not found: {pdf_path}")

        extract_text_from_pdf(pdf_path)

    except Exception as e:
        print("[FATAL] Error in extract_text.py:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
