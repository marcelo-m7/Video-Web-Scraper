import logging
from typing import List
import requests
from bs4 import BeautifulSoup
from .config import HEADERS

logger = logging.getLogger(__name__)


class VideoScraper:
    """Responsável por obter e parsear a página de resultados."""

    def __init__(self, http_client: requests.Session | None = None) -> None:
        self.http = http_client or requests.Session()
        self.http.headers.update(HEADERS)

    def fetch_html(self, url: str) -> str:
        logger.info("Baixando HTML da página: %s", url)
        resp = self.http.get(url, timeout=30)
        resp.raise_for_status()
        return resp.text

    def extract_video_urls(self, html: str) -> List[str]:
        """Devolve uma lista de URLs absolutas dos vídeos."""
        logger.info("Extraindo URLs dos vídeos do HTML")
        soup = BeautifulSoup(html, "html.parser")

        # Exemplo genérico: ajuste o seletor conforme o site real
        anchors = soup.select("a[href$='.mp4'], source[src$='.mp4']")

        urls: list[str] = []
        for tag in anchors:
            url = tag.get("href") or tag.get("src")
            if url:
                urls.append(url)

        logger.info("Encontrados %d vídeos", len(urls))
        return urls