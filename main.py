import os


def configurar_diretorios():
    caminhos = {
        "animes": os.path.join(
            os.path.expandvars(r"%userprofile%"), "Desktop", "Animes_teste"
        )
    }
    for pasta in (i for i in caminhos.values()):
        os.makedirs(pasta, exist_ok=True)
    os.environ.update({"caminho": caminhos["animes"]})


configurar_diretorios()
import sys
from multiprocessing import freeze_support
from datetime import datetime
import asyncio
import logging
from PIL import Image
import io
import re
import pandas as pd
from shutil import rmtree
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Label, RichLog, Static
from textual.containers import Vertical, Container
from textual import work
from rich_pixels import Pixels


class CustomHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            os.startfile("log.log")
            sys.exit()


versao = "v1.3"
from nucleo import core


class AnimeDownloaderTUI(App):
    CSS_PATH = "estilo.tcss"
    BINDINGS = [("p", "pesquisa", "Pesquisar"), ("h", "home", "Home")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield RichLog(id="frame_log")

    async def on_mount(self):
        self.title = "Anime Downloader " + versao
        self.animes = None
        self.carregar_dados()

    @work(exclusive=True)
    async def carregar_dados(self):
        painel_logs = self.query_one("#frame_log", RichLog)

        def registrar(texto: str):
            painel_logs.write(texto)

        registrar("Procurando arquivo...")
        if os.path.exists("dados.parquet"):
            registrar("Arquivo encontrado")
            await asyncio.sleep(1)
            registrar("Carregando dados do arquivo...")
            with open("dados.parquet", "rb") as arquivo:
                self.animes = pd.read_parquet(arquivo)
            registrar("Arquivo carregado")
        else:
            pass
        self.animes.sort_index(inplace=True)
        self.menu_principal()

    def menu_principal(self):
        self.query_one("#frame_log", RichLog).display = False
        # painel = self.query_one("#frame_log", RichLog)
        try:
            painel_animes = self.query_one("#painel_animes", Container)
        except Exception:
            painel_animes = Container(id="painel_animes")
            self.mount(painel_animes)
            for nome, anime in self.animes.iterrows():
                imagem_poster = Image.open(io.BytesIO(anime["imagem"]))
                largura_caractere = 24
                proporcao = largura_caractere / imagem_poster.width
                nova_largura = largura_caractere
                nova_altura = int(imagem_poster.height * proporcao)
                imagem_poster = imagem_poster.resize((nova_largura, nova_altura))
                imagem_poster = Pixels.from_image(imagem_poster)
                poster = Static(imagem_poster, classes="poster")
                nome = Label(nome.__str__(), classes="nome_anime")
                cartao = Vertical(poster, nome, classes="cartao-anime")
                painel_animes.mount(cartao)
        else:
            pass


if __name__ == "__main__":
    freeze_support()
    logging.basicConfig(
        filename="log.log",
        filemode="w",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger()
    logger.addHandler(CustomHandler())
    core.verificar_navegador()
    core.verificar_ffmpeg()
    asyncio.run(core.verifica_cookies())
    app = AnimeDownloaderTUI()
    app.run()
    # os.startfile("log.log")
