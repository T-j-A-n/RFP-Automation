# =====================================
# main.py — EY Techathon End-to-End Demo
# =====================================

# --- Imports ---
import os
import csv
import pandas as pd
from agents.scraper_agent_playwright import download_pdf_playwright
from agents.parser_agent import ParserAgent
from agents.technical_agent import TechnicalAgent
from agents.ocr_agent import OcrAgent
from sklearn.feature_extraction.text import CountVectorizer

# --- Step 1: Define folders ---
DATA_DIR = "data"
RFP_DIR = os.path.join(DATA_DIR, "rfps")
PARSED_CSV = os.path.join(DATA_DIR, "parsed_rfps.csv")
os.makedirs(RFP_DIR, exist_ok=True)

# --- Step 2: Verified public PDF URLs ---
pdf_links = [
    "https://epi.gov.in/admin/image/tenders/1709123994_NITETS202.pdf",
    "https://education.gov.in/sites/upload_files/mhrd/files/tenders/tender.pdf",
    "https://www.iitk.ac.in/dord/tender/tender_document.pdf"
]

# --- Step 2.5: OCR Agent (convert scanned PDFs to text-based PDFs) ---
print("\n==============================")
print("👁️  STEP 2.5: Running OCR on downloaded PDFs")
print("==============================\n")

ocr_agent = OcrAgent(input_dir=RFP_DIR)
processed_files = ocr_agent.run()

# --- Step 3: Download the PDFs ---
print("\n==============================")
print("📥 STEP 3: Downloading Tender PDFs")
print("==============================\n")

downloaded_files = []
for link in pdf_links:
    print(f"➡️  Attempting to download: {link}")
    path = download_pdf_playwright(link, out_dir=RFP_DIR, headless=True)
    if path:
        downloaded_files.append(path)
    else:
        print(f"⚠️  Failed to download: {link}")

# --- Step 4: Extract text using ParserAgent ---
print("\n==============================")
print("📄 STEP 4: Extracting Text from PDFs")
print("==============================\n")

parser = ParserAgent(input_dir=RFP_DIR)
parsed_data = parser.run()

# --- Step 5: Save parsed text to CSV ---
print("\n==============================")
print("💾 STEP 5: Saving Extracted Data to CSV")
print("==============================\n")

os.makedirs(DATA_DIR, exist_ok=True)
with open(PARSED_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Filename", "Extracted_Text"])
    for item in parsed_data:
        writer.writerow([item["file"], item["text"]])

print(f"✅ CSV saved: {PARSED_CSV}")

# --- Step 6: NLP Analysis on Extracted Text ---
print("\n==============================")
print("🧠 STEP 6: NLP Analysis on Extracted PDF Text")
print("==============================\n")

# Read parsed text from CSV
parsed_df = pd.read_csv(PARSED_CSV)
text_content = " ".join(parsed_df["Extracted_Text"].astype(str).tolist())

# --- Keyword Extraction ---
vectorizer = CountVectorizer(stop_words='english')
word_counts = vectorizer.fit_transform([text_content])
words = vectorizer.get_feature_names_out()
frequencies = word_counts.toarray()[0]
word_freq = sorted(zip(words, frequencies), key=lambda x: x[1], reverse=True)[:10]

print("\n🔍 Top Keywords Found in Extracted PDFs:")
for word, freq in word_freq:
    print(f"- {word}: {freq}")

# --- Simple Insight Extraction ---
summary_lines = [line for line in text_content.split("\n") if "-" in line or line.strip().startswith(("1.", "2.", "3.", "4.", "5."))]
print("\n🧩 Extracted Key Insights from PDFs:")
for line in summary_lines[:10]:
    print(line)

# --- Save NLP Insights ---
NLP_CSV = os.path.join(DATA_DIR, "pdf_insights.csv")
with open(NLP_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Keyword", "Frequency"])
    writer.writerows(word_freq)

print(f"\n✅ NLP insights saved: {NLP_CSV}")

# --- Step 7: Technical Matching ---
print("\n==============================")
print("🧩 STEP 7: Matching Tender Specs to Internal SKUs")
print("==============================\n")

tech_agent = TechnicalAgent(
    parsed_csv=PARSED_CSV,
    products_csv=os.path.join(DATA_DIR, "products.csv")
)
matched_df = tech_agent.run(threshold=40)

print(f"\n✅ Found {len(matched_df)} total matches saved in data/matched_tenders.csv")

# --- Step 8: Final Summary ---
print("\n==============================")
print("🏁 PROCESS COMPLETE")
print("==============================\n")

if downloaded_files:
    print(f"✅ {len(downloaded_files)} PDF(s) downloaded, parsed, and analyzed successfully.")
else:
    print("❌ No PDFs were downloaded. Check links or network.")

print("\nNext Step: Feed parsed_rfps.csv and pdf_insights.csv into your TechnicalAgent and PricingAgent 🔄")

# --- STEP 4: Technical Agent ---
from agents.technical_agent import TechnicalAgent
tech = TechnicalAgent(parsed_csv="data/parsed_rfps.csv", products_csv="data/products.csv")
matched_df = tech.run(threshold=40)

# --- STEP 5: Pricing Agent ---
from agents.pricing_agent import PricingAgent
price = PricingAgent(matches_csv="data/matched_tenders.csv",
                     parsed_csv="data/parsed_rfps.csv")
price_df = price.run(margin_pct=10)
