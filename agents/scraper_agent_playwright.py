from playwright.sync_api import sync_playwright
import os, time, fitz
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

def download_pdf_playwright(pdf_url: str, out_dir: str = "data/rfps", headless: bool = True):
    """
    Downloads a PDF using Playwright and applies OCR automatically
    if no text layer is found (for scanned tenders).
    """

    os.makedirs(out_dir, exist_ok=True)
    file_name = pdf_url.split("/")[-1].split("?")[0] or f"tender_{int(time.time())}.pdf"
    save_path = os.path.join(out_dir, file_name)

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=headless)
        page = browser.new_page()

        try:
            # ✅ Expect download (instead of page.goto)
            with page.expect_download() as dl_info:
                page.evaluate(f"window.open('{pdf_url}', '_blank')")
            download = dl_info.value
            download.save_as(save_path)
            print(f"📄 Downloaded: {save_path}")

            # Check if PDF has text
            if not pdf_has_text(save_path):
                print(f"🧠 Running OCR on {file_name} (scanned tender detected)...")
                ocr_pdf(save_path)
                print(f"✅ OCR complete for {file_name}")

            browser.close()
            return save_path

        except Exception as e:
            print(f"❌ Failed to download {pdf_url}: {e}")
            browser.close()
            return None


def pdf_has_text(pdf_path):
    """Checks if the PDF already has text content."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text")
        doc.close()
        return len(text.strip()) > 50
    except Exception:
        return False


def ocr_pdf(pdf_path):
    """Runs OCR on a scanned PDF and replaces it with a text-searchable version."""
    images = convert_from_path(pdf_path, dpi=300)
    ocr_text = ""

    for img in images:
        ocr_text += pytesseract.image_to_string(img)

    # Create a new searchable PDF
    new_pdf = fitz.open()
    page = new_pdf.new_page()
    page.insert_text((50, 50), ocr_text[:5000])  # embed first chunk for searchability
    new_path = pdf_path.replace(".pdf", "_ocr.pdf")
    new_pdf.save(new_path)
    new_pdf.close()

    # Replace old with OCR’d file
    os.remove(pdf_path)
    os.rename(new_path, pdf_path)
    return pdf_path
