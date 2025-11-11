import pandas as pd
from rapidfuzz import fuzz
import os

class TechnicalAgent:
    """
    Matches parsed tender descriptions with internal SKUs
    using fuzzy matching and keyword-based relevance scoring.
    """

    def __init__(self, parsed_csv="data/parsed_rfps.csv", products_csv="data/products.csv"):
        if not os.path.exists(parsed_csv):
            raise FileNotFoundError("❌ Missing parsed_rfps.csv")
        if not os.path.exists(products_csv):
            raise FileNotFoundError("❌ Missing products.csv")

        self.rfps = pd.read_csv(parsed_csv)
        self.products = pd.read_csv(products_csv)

    def run(self, threshold=40):
        results = []
        for _, row in self.rfps.iterrows():
            tender_name = row["Filename"]
            tender_text = str(row.get("Extracted_Text", "")).lower()

            for _, prod in self.products.iterrows():
                product_name = str(prod["Product_Name"]).lower()
                score = fuzz.token_set_ratio(product_name, tender_text)
                if score >= threshold:
                    results.append({
                        "Tender_File": tender_name,
                        "Product_Name": prod["Product_Name"],
                        "Match_Score": score,
                        "Base_Price": prod.get("Base_Price", 0),
                        "Category": prod.get("Category", "Unknown")
                    })
        df = pd.DataFrame(results)
        out_path = "data/matched_tenders.csv"
        #df.to_csv(out_path, index=False)
        print(f"✅ TechnicalAgent complete. Saved matches to {out_path}")
        return df
