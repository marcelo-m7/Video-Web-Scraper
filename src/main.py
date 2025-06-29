import logging
from pathlib import Path

import click

from .scraper import VideoScraper
from .selector import VideoSelector
from .downloader import VideoDownloader
from .config import DOWNLOAD_DIR


logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)


@click.command()
@click.argument("url")
@click.option(
    "--no-convert/--convert",
    default=True,
    help="Desativa ou ativa a conversão para .mp4 (default: ativa).",
)
@click.option(
    "--out-dir",
    default=DOWNLOAD_DIR,
    type=click.Path(file_okay=False),
    help=f"Diretório de saída (default: {DOWNLOAD_DIR}).",
)
def cli(url: str, no_convert: bool, out_dir: str) -> None:
    """Baixa vídeos públicos de uma URL de pesquisa/playlist."""
    scraper = VideoScraper()
    html = scraper.fetch_html(url)
    video_urls = scraper.extract_video_urls(html)

    if not video_urls:
        click.echo("Nenhum vídeo encontrado!")
        return

    chosen = VideoSelector.choose(video_urls)

    if not chosen:
        click.echo("Nenhum vídeo selecionado.")
        return

    downloader = VideoDownloader(
        download_dir=Path(out_dir),
        convert_to_mp4=not no_convert,
    )
    downloader.download_all(chosen)


if __name__ == "__main__":
    cli()