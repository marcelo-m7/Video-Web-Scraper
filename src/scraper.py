import logging
from typing import List, Optional, cast
import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin
from config import HEADERS
import re

logger = logging.getLogger(__name__)

class VideoScraper:
    """Responsável por obter e parsear a página de resultados e de cada post."""

    BASE_URL = "https://www.tiktok.com"

    def __init__(self, http_client: Optional[requests.Session] = None) -> None:
        self.http = http_client or requests.Session()
        self.http.headers.update(HEADERS)

    def fetch_html(self, url: str) -> str:
        logger.info("Baixando HTML da página: %s", url)
        resp = self.http.get(url, timeout=30)
        resp.raise_for_status()
        return resp.text

    def extract_post_urls(self, html: str) -> list[str]:
        """
        Encontra todos os <a class="thumb__link"> dentro de um .thumb[data-isvideo="1"]
        e filtra aqueles cujo href bate com /p/<números>.
        """
        soup = BeautifulSoup(html, "html.parser")
        thumbs = soup.select("div.thumb[data-isvideo='1']")
        posts: list[str] = []
        patt = re.compile(r"/p/\d+")

        for thumb in thumbs:
            a = thumb.find("a", class_="thumb__link")
            if not isinstance(a, Tag):
                continue

            href = a.get("href")
            if isinstance(href, str) and patt.search(href):
                full = urljoin(self.BASE_URL, href)
                posts.append(full)

        logger.info("Encontrados %d posts de vídeo", len(posts))
        return posts

    def extract_video_url_from_post(self, post_url: str) -> Optional[str]:
        """
        Visita o post e devolve a URL .mp4 (cuida de <video src> e <source src>).
        Pós-processa para lidar com query-strings como '?tag=16'.
        """
        html = self.fetch_html(post_url)
        soup = BeautifulSoup(html, "html.parser")

        raw_video = soup.find("video")
        if not isinstance(raw_video, Tag):
            logger.warning("Nenhum <video> em %s", post_url)
            return None

        video_tag: Tag = cast(Tag, raw_video)          # convencemos o type-checker

        # 1) src direto no <video>
        src_attr = video_tag.get("src")
        if isinstance(src_attr, str) and ".mp4" in src_attr:
            return urljoin(post_url, src_attr)

        # 2) src dentro de <source>
        for node in video_tag.find_all("source"):
            if not isinstance(node, Tag):              # garante .get()
                continue
            src = node.get("src")
            if isinstance(src, str) and ".mp4" in src:
                return urljoin(post_url, src)

        logger.warning("Não achei URL .mp4 em %s", post_url)
        return None
    
    # def extract_video_url_from_post(self, post_url: str) -> Optional[str]:
    #     """
    #     Acessa o post e extrai o URL direto do .mp4.
    #     Ajuste o seletor conforme o HTML real do player.
    #     """
    #     html = self.fetch_html(post_url)
    #     soup = BeautifulSoup(html, "html.parser")

    #     # 1) Tenta encontrar <video src="...">
    #     video_tag = soup.find("video")
    #     if isinstance(video_tag, Tag):
    #         src = video_tag.get("src")
    #         if isinstance(src, str) and src.endswith(".mp4"):
    #             return urljoin(post_url, src)

    #     # 2) (Exemplo) Se estiver embutido num JSON dentro de <script>
    #     #    você teria algo como:
    #     #    scripts = soup.find_all("script")
    #     #    for sc in scripts:
    #     #        m = JSON_REGEX.search(sc.string or "")
    #     #        ...

    #     logger.warning("Não achei URL .mp4 em %s", post_url)
    #     return None

    def extract_all_video_urls(self, listing_url: str) -> List[str]:
        """
        Faz todo o fluxo: baixa a página de listagem, pega os posts
        e extrai os .mp4 de cada um.
        """
        html = self.fetch_html(listing_url)
        post_urls = self.extract_post_urls(html)

        video_urls: List[str] = []
        for pu in post_urls:
            v = self.extract_video_url_from_post(pu)
            if v:
                video_urls.append(v)

        logger.info("No total, %d URLs de vídeo extraídas", len(video_urls))
        return video_urls
