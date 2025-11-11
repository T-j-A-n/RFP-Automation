import pandas as pd
import os

class PricingAgent:
    """
    Combines matched products and tender metadata to
    generate bid-ready pricing sheet.
    """

    def __init__(self,
                 matches_csv="data/matched_tenders.csv",
                 parsed_csv="data/parsed_rfps.csv",
                 out_xlsx="data/bid_pricing.xlsx"):
        if not os.path.exists(matches_csv):
            raise FileNotFoundError("❌ Missing matched_tenders.csv")
        if not os.path.exists(parsed_csv):
            raise FileNotFoundError("❌ Missing parsed_rfps.csv")

        self.matches = pd.read_csv(matches_csv)
        self.parsed = pd.read_csv(parsed_csv)
        self.out_xlsx = out_xlsx

    def run(self, margin_pct=10):
        results = []
        for _, match in self.matches.iterrows():
            tender_name = match["Tender_File"]
            tender_meta = self.parsed[self.parsed["Filename"] == tender_name]

            tender_fee = 0
            emd = 0
            if not tender_meta.empty:
                fee_val = tender_meta.iloc[0].get("Tender_Fee", "")
                emd_val = tender_meta.iloc[0].get("EMD", "")
                tender_fee = extract_number(fee_val)
                emd = extract_number(emd_val)

            base_price = float(match.get("Base_Price", 0))
            bid_price = base_price * (1 + margin_pct / 100)

            total_estimate = bid_price + tender_fee + emd

            results.append({
                "Tender_File": tender_name,
                "Product_Name": match["Product_Name"],
                "Category": match["Category"],
                "Match_Score": match["Match_Score"],
                "Base_Price": base_price,
                "Bid_Price": bid_price,
                "Tender_Fee": tender_fee,
                "EMD": emd,
                "Total_Estimate": total_estimate
            })

        df = pd.DataFrame(results)
        df.to_excel(self.out_xlsx, index=False)
        print(f"✅ PricingAgent complete. Saved: {self.out_xlsx}")
        return df


def extract_number(text):
    """Helper to extract numeric value from strings like 'Rs. 2000/-'."""
    import re
    try:
        numbers = re.findall(r"[\d,]+", str(text))
        if not numbers:
            return 0
        return float(numbers[0].replace(",", ""))
    except Exception:
        return 0
