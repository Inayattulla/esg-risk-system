import sys
import os
import fitz  # PyMuPDF
import traceback

def extract_text_from_pdf(pdf_path, save_to_file=True, max_pages=100):
    try:
        if not os.path.exists(pdf_path):
            print(f"[ERROR] File not found: {pdf_path}")
            return ""
        
        with fitz.open(pdf_path) as doc:
            print(f"[INFO] Opened {pdf_path} with {len(doc)} pages")
            full_text = ""
            for page_num, page in enumerate(doc, start=1):
                if page_num > max_pages:
                    print(f"[INFO] Page limit {max_pages} reached, stopping extraction.")
                    break
                text = page.get_text()
                full_text += text + "\n"
                print(f"[INFO] Page {page_num}: {'Text found' if text.strip() else 'No text found'}")


        if not full_text.strip():
            print("[WARNING] No extractable text found in the PDF.")
            return ""
        
        if save_to_file:
            outpath = os.path.join("/tmp", "extracted_text.txt")  # ✅ use /tmp
            with open(outpath, "w", encoding="utf-8") as f:
                f.write(full_text)
            print(f"[SUCCESS] Extracted text saved to {outpath}")

        return full_text

    except Exception as e:
        print("[EXCEPTION] Error in extract_text.py:")
        traceback.print_exc()
        return ""

# CLI usage
if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            raise ValueError("PDF path not provided to extract_text.py")

        pdf_path = sys.argv[1]
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"[ERROR] File not found: {pdf_path}")

        text = extract_text_from_pdf(pdf_path, save_to_file=True)
        if text.strip():
            print("[CLI] Extraction complete, text length:", len(text))


    except Exception as e:
        print("[FATAL] Error in extract_text.py:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
