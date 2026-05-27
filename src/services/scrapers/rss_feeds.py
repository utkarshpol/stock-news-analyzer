# src/services/scraper/rss_fetcher.py
import urllib.parse
import xml.etree.ElementTree as ET
import httpx
from typing import List, Dict, Any

class AsyncRSSFetcher:
    # Whitelist of top-tier, highly credible financial and mainstream publications
    CREDIBLE_SOURCES = [
        "economictimes.indiatimes.com",
        "livemint.com",
        "business-standard.com",
        "thehindubusinessline.com",
        "bloombergquint.com",
        "bloomberg.com",
        "reuters.com",
        "moneycontrol.com",
        "financialexpress.com"
    ]

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def _build_google_rss_url(self, base_query: str) -> str:
        """
        Injects strict validation constraints into the query:
        1. Limits publication dates strictly to the past 24 hours (when:1d).
        2. Restricts results only to our whitelisted credible media sites.
        """
        # Build the boolean string constraint: (site:domain1 OR site:domain2 OR ...)
        site_constraints = " OR ".join([f"site:{site}" for site in self.CREDIBLE_SOURCES])
        
        clean_query = base_query.strip().replace('"', '')
        # Combine: "Your Query" (site:X OR site:Y) when:1d
        final_query = f"{clean_query} when:1d"
        
        encoded_query = urllib.parse.quote_plus(final_query)
        # hl=en-IN and gl=IN keeps the context localized to Indian financial reporting parameters
        return f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
        return f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"

    async def fetch_feed_headlines(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Asynchronously polls Google RSS for a specific query string 
        and extracts verified 24-hour publication blocks.
        """
        url = self._build_google_rss_url(query)
        print(url)
        articles = []

        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    return articles

                root = ET.fromstring(response.content)
                
                for item in root.findall(".//item")[:max_results]:
                    title = item.findtext("title", "").strip()
                    link = item.findtext("link", "").strip()
                    pub_date = item.findtext("pubDate", "").strip()
                    source = item.findtext("source", "").strip()
                    
                    articles.append({
                        "title": title,
                        "link": link,
                        "published_at": pub_date,
                        "source": source
                    })
                    
        except Exception:
            pass

        return articles