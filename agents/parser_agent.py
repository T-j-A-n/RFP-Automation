# agents/parser_agent.py
import fitz, os

class ParserAgent:
    def __init__(self, input_dir="/Users/tejasanand/Desktop/RFP Automation/data/rfps"):
        self.input_dir = input_dir

    def run(self):
        extracted_data = []
        for file in os.listdir(self.input_dir):
            if file.lower().endswith(".pdf"):
                path = os.path.join(self.input_dir, file)
                print(f"📄 Parsing {file}...")
                text = self.extract_text(path)
                extracted_data.append({"file": file, "text": text[:1000]})
        return extracted_data

    def extract_text(self, pdf_path):
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text")
        doc.close()
        return text
