# agents/ocr_agent.py
import fitz
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import os

class OcrAgent:
    """
    OCR Agent:
    - Checks each PDF for text content
    - Runs OCR on scanned (image-only) PDFs
    - Produces a searchable (text-embedded) PDF
    """

    def __init__(self, input_dir="data/rfps", output_dir=None):
        self.input_dir = input_dir
        self.output_dir = output_dir or input_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def has_text(self, pdf_path):
        """Check if the PDF already has selectable text."""
        try:
            doc = fitz.open(pdf_path)
            text = "".join(page.get_text("text") for page in doc)
            doc.close()
            return len(text.strip()) > 30
        except Exception:
            return False

    def run_ocr(self, pdf_path):
        """Perform OCR on image-based PDF and save new searchable copy."""
        try:
            images = convert_from_path(pdf_path, dpi=300)
            pdf_writer = fitz.open()

            for img in images:
                text = pytesseract.image_to_string(img)
                pix = fitz.Pixmap(fitz.csRGB, img.width, img.height, 8)
                pdf_page = pdf_writer.new_page(width=img.width, height=img.height)
                pdf_page.insert_text((20, 20), text[:2000])  # embed recognized text
            ocr_path = os.path.join(self.output_dir, os.path.basename(pdf_path).replace(".pdf", "_ocr.pdf"))
            pdf_writer.save(ocr_path)
            pdf_writer.close()
            print(f"🧠 OCR complete: {ocr_path}")
            return ocr_path
        except Exception as e:
            print(f"⚠️ OCR failed for {pdf_path}: {e}")
            return None

    def run(self):
        """Run OCR on all PDFs in folder."""
        processed_files = []
        for file in os.listdir(self.input_dir):
            if not file.lower().endswith(".pdf"):
                continue
            pdf_path = os.path.join(self.input_dir, file)

            if self.has_text(pdf_path):
                print(f"✅ {file} already has text; skipping OCR.")
                processed_files.append(pdf_path)
            else:
                print(f"🧾 {file} has no text layer — performing OCR...")
                ocr_file = self.run_ocr(pdf_path)
                if ocr_file:
                    processed_files.append(ocr_file)

        print(f"\n✅ OCR Agent complete. Total processed files: {len(processed_files)}")
        return processed_files
