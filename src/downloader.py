import logging
import subprocess
from pathlib import Path
from typing import Iterable

import requests
from tqdm import tqdm

from config import CHUNK_SIZE, DOWNLOAD_DIR, HEADERS

logger = logging.getLogger(__name__)


class VideoDownloader:
    """Baixa (e opcionalmente converte) vídeos."""

    def __init__(
        self,
        download_dir: str | Path = DOWNLOAD_DIR,
        http_client: requests.Session | None = None,
        convert_to_mp4: bool = True,
    ) -> None:
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.http = http_client or requests.Session()
        self.http.headers.update(HEADERS)
        self.convert = convert_to_mp4

    def download_all(self, urls: Iterable[str]) -> None:
        for url in urls:
            self._download_one(url)

    def _download_one(self, url: str) -> None:
        file_name = url.split("/")[-1].split("?")[0]
        dest = self.download_dir / file_name

        logger.info("Iniciando download: %s -> %s", url, dest)

        with self.http.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))

            with open(dest, "wb") as f, tqdm(
                total=total,
                unit="B",
                unit_scale=True,
                desc=file_name,
            ) as bar:
                for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))

        logger.info("Download finalizado: %s", dest)

        if self.convert and dest.suffix.lower() != ".mp4":
            self._convert_to_mp4(dest)

    def _convert_to_mp4(self, src: Path) -> None:
        dst = src.with_suffix(".mp4")
        logger.info("Convertendo %s => %s", src.name, dst.name)
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            str(dst),
        ]
        subprocess.run(cmd, check=True)
        logger.info("Conversão concluída: %s", dst)