# agents/scraper_agent.py
import requests, time, random, logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class ScraperAgent:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def polite_get(self, url):
        try:
            r = self.session.get(url, headers=self.headers, timeout=25)
            if r.status_code in (403, 404):
                logger.warning(f"Blocked or missing: {url} ({r.status_code})")
                return ""
            time.sleep(random.uniform(1.5, 3.0))
            return r.text
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
            return ""

    def find_tender_pages(self, html, base_url):
        """Find tender detail page URLs (second-level links)."""
        soup = BeautifulSoup(html, "html.parser")
        tender_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "TenderDetails" in href or "tnid=" in href:
                tender_links.append(urljoin(base_url, href))
        return list(set(tender_links))

    def find_pdf_links(self, html, base_url):
        """Extract document/PDF download links from a tender detail page."""
        soup = BeautifulSoup(html, "html.parser")
        pdfs = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True).lower()
            if href.lower().endswith(".pdf") or "TenderDocuments" in href or "bid document" in text:
                pdfs.append(urljoin(base_url, href))
        return list(set(pdfs))

    def run(self, portal_url="https://etenders.gov.in/eprocure/app?page=FrontEndLatestActiveTenders&service=page"):
        logger.info(f"🔍 Fetching tender list from {portal_url}")
        main_html = self.polite_get(portal_url)
        tender_pages = self.find_tender_pages(main_html, portal_url)
        logger.info(f"Found {len(tender_pages)} tender detail pages")

        all_rfps = []
        for t_url in tender_pages[:10]:  # limit for demo
            logger.info(f"➡️ Visiting tender: {t_url}")
            tender_html = self.polite_get(t_url)
            pdfs = self.find_pdf_links(tender_html, t_url)
            for pdf in pdfs:
                all_rfps.append({
                    "title": t_url.split("tnid=")[-1],
                    "pdf_url": pdf,
                    "source": t_url
                })
        unique = {r["pdf_url"]: r for r in all_rfps}.values()
        return {"status": "ok", "payload": list(unique)}
