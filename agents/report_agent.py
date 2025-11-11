# agents/report_agent.py
import pandas as pd, logging
from jinja2 import Environment, FileSystemLoader
import xlsxwriter
logger = logging.getLogger(__name__)

class ReportAgent:
    def __init__(self, out_dir="data/output"):
        self.out_dir = out_dir

    def run(self, priced_payload, rfp_meta, company_meta, out_basename="proposal"):
        items = priced_payload['items']
        summary = priced_payload['summary']
        excel_path = f"{self.out_dir}/{out_basename}.xlsx"
        df = pd.DataFrame(items)
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            # cover sheet
            cover = pd.DataFrame([{"RFP Title": rfp_meta.get("title"), "Due Date": rfp_meta.get("due_date")}])
            cover.to_excel(writer, sheet_name="Cover", index=False)
            df.to_excel(writer, sheet_name="Price_Breakup", index=False)
            summary_df = pd.DataFrame([summary])
            summary_df.to_excel(writer, sheet_name="Summary", index=False)
        # Optionally render PDF via HTML templates
        return {"status":"ok", "payload":{"excel": excel_path}}
