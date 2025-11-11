# agents/backbone_agent.py
import logging
from .scrapper_agent import ScraperAgent
from .parser_agent import ParserAgent
from .technical_agent import TechnicalAgent
from .pricing_agent import PricingAgent
from .report_agent import ReportAgent

logger = logging.getLogger(__name__)

class BackboneAgent:
    def __init__(self, sku_csv="data/products.csv", price_csv="data/pricing.csv"):
        self.scraper = ScraperAgent()
        self.parser = ParserAgent()
        self.tech = TechnicalAgent(sku_csv)
        self.pricing = PricingAgent(price_csv)
        self.report = ReportAgent()

    def run_pipeline(self, portal_urls):
        scraped = self.scraper.run(portal_urls)
        outputs = []
        for r in scraped['payload']:
            try:
                parsed = self.parser.run(pdf_url=r['pdf_url'])
                specs = parsed['payload']['spec_sections']
                matches = self.tech.run(specs)
                priced = self.pricing.run([m for m in matches['payload']])
                report = self.report.run(priced['payload'], rfp_meta={"title": r.get("title"), "due_date": parsed['payload'].get("due_date")}, company_meta={})
                outputs.append({"rfp": r, "report": report})
            except Exception as e:
                logger.exception("Failed pipeline for %s", r.get('pdf_url'))
                outputs.append({"rfp": r, "error": str(e)})
        return outputs
