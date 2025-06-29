from typing import List


class VideoSelector:
    """Permite ao usuário escolher quais vídeos baixar."""

    @staticmethod
    def choose(urls: List[str]) -> List[str]:
        for idx, u in enumerate(urls, 1):
            print(f"[{idx:02}] {u}")

        choices = input(
            "\nDigite os números desejados separados por vírgula (ex: 1,3,5) "
            "ou ENTER para baixar todos: "
        ).strip()

        if not choices:
            return urls

        selected: list[str] = []
        for part in choices.split(","):
            try:
                i = int(part) - 1
                selected.append(urls[i])
            except (ValueError, IndexError):
                print(f"Ignorando entrada inválida: {part}")

        return selected