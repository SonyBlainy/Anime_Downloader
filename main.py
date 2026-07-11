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
from textual.widgets import Footer, Header, Label, RichLog, Static, Input
from textual.containers import Vertical, Container, Horizontal
from textual import work, on
from textual.binding import Binding
from textual.reactive import reactive
from rich_pixels import Pixels


class CustomHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            os.startfile("log.log")
            sys.exit()


versao = "v1.3"
from nucleo import core


class AnimePoster(Static):
    def __init__(self, renderizavel, series: pd.Series, *args, **kwars) -> None:
        super().__init__(renderizavel, *args, **kwars)
        self.anime_series = series


class AnimeDownloaderTUI(App):
    CSS_PATH = "estilo.tcss"
    BINDINGS = [
        ("p", "pesquisa", "Pesquisar"),
        ("h", "home", "Home"),
        ("q", "sair", "Sair"),
        Binding("escape", "desfoco", show=False),
        Binding("right", "direita", show=False),
        Binding("left", "esquerda", show=False),
        Binding("up", "cima", show=False),
        Binding("down", "baixo", show=False),
        Binding("enter", "enter", show=False),
    ]
    ENABLE_COMMAND_PALETTE = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield RichLog(id="frame_log")

    async def on_mount(self):
        self.title = "Anime Downloader " + versao
        self.theme = "tokyo-night"
        self.carregar_dados()

    def action_direita(self):
        posters = self.query(
            ".poster",
        )
        for i, p in enumerate(posters):
            if "selecionado" in p.classes:
                poster_selecionado = p
                n = i
                break
        if n + 1 < len(posters):
            poster_selecionado.remove_class("selecionado")
            posters[n + 1].add_class("selecionado")
            posters[n + 1].parent.scroll_visible()

    def action_esquerda(self):
        posters = self.query(
            ".poster",
        )
        for i, p in enumerate(posters):
            if "selecionado" in p.classes:
                poster_selecionado = p
                n = i
                break
        if n - 1 >= 0:
            poster_selecionado.remove_class("selecionado")
            posters[n - 1].add_class("selecionado")
            posters[n - 1].parent.scroll_visible()

    def action_cima(self):
        posters = self.query(
            ".poster",
        )
        for i, p in enumerate(posters):
            if "selecionado" in p.classes:
                poster_selecionado = p
                n = i
                break
        if n - 5 >= 0:
            poster_selecionado.remove_class("selecionado")
            posters[n - 5].add_class("selecionado")
            posters[n - 5].parent.scroll_visible()

    def action_baixo(self):
        posters = self.query(
            ".poster",
        )
        for i, p in enumerate(posters):
            if "selecionado" in p.classes:
                poster_selecionado = p
                n = i
                break
        if n + 5 < len(posters):
            poster_selecionado.remove_class("selecionado")
            posters[n + 5].add_class("selecionado")
            posters[n + 5].parent.scroll_visible()

    def action_enter(self):
        anime_frame = self.query_one(".painel_animes", Container)
        anime_frame.display = False
        anime = self.query_one(".selecionado", AnimePoster)
        self.query_one(".n_animes_frame").remove()
        anime_frame.remove()
        imagem_poster = Image.open(io.BytesIO(anime.anime_series["imagem"]))
        largura_caractere = 42
        proporcao = largura_caractere / imagem_poster.width
        nova_largura = largura_caractere
        nova_altura = int(imagem_poster.height * proporcao)
        imagem_poster = Pixels.from_image(
            imagem_poster, resize=(nova_largura, nova_altura)
        )
        imagem_poster = Static(imagem_poster, classes="poster")
        nome = anime.anime_series.name
        nome = Label(nome.__str__(), id="nome_anime")
        anime_info_frame = Container(imagem_poster, nome, id="anime_info_frame")
        self.mount(anime_info_frame)

    def action_sair(self):
        self.exit()

    def action_desfoco(self):
        self.set_focus(None)

    def action_pesquisa(self):
        try:
            self.query_one(".n_animes_frame").remove()
        except Exception:
            pass
        painel_animes = self.query_one(".painel_animes", Container)
        painel_animes.display = False
        try:
            pesquisa_input = self.query_one("#pesquisa", Input)
        except Exception:
            pesquisa_input = Input(
                placeholder="Digite o nome do anime...", id="pesquisa"
            )
            self.mount(pesquisa_input)
            pesquisa_input.focus()
            painel_animes.remove()

    async def action_home(self):
        try:
            await self.query_one("#pesquisa", Input).remove()
        except Exception:
            pass
        await self.exibir_animes()

    @on(Input.Submitted, "#pesquisa")
    async def pesquisar(self, evento: Input.Submitted):
        pesquisa_input = self.query_one("#pesquisa", Input)
        pesquisa_input.display = False
        animes = await core.pesquisar(evento.value)
        pesquisa_input.remove()
        await self.exibir_animes(animes, True)

    @work(exclusive=True)
    async def carregar_dados(self):
        painel_logs = self.query_one("#frame_log", RichLog)

        def registrar(texto: str):
            painel_logs.write(texto)

        registrar("Procurando arquivo...")
        if os.path.exists("dados.parquet"):
            registrar("Arquivo encontrado")
            registrar("Carregando dados do arquivo...")
            with open("dados.parquet", "rb") as arquivo:
                self.animes = pd.read_parquet(arquivo)
            registrar("Arquivo carregado")
        else:
            pass
        self.animes.sort_index(inplace=True)
        await self.exibir_animes()

    async def exibir_animes(self, animes: None | pd.DataFrame = None, pesquisa=False):
        if not pesquisa:
            try:
                self.query_one("#frame_log", RichLog).remove()
            except Exception:
                pass
            animes = self.animes.copy()
        try:
            self.query_one(".n_animes_frame", Horizontal).remove()
        except Exception:
            pass
        else:
            await self.query_one(".painel_animes", Container).remove()
        n_animes_label = Label(f"{len(animes)} Animes", classes="n_animes")
        n_animes_container = Horizontal(n_animes_label, classes="n_animes_frame")
        self.mount(n_animes_container)
        try:
            painel_animes = self.query_one(".painel_animes", Container)
        except Exception:
            painel_animes = Container(classes="painel_animes")
            self.mount(painel_animes)
        else:
            painel_animes.query().remove()
            painel_animes.display = True
        for i, (nome, anime) in enumerate(animes.iterrows()):
            imagem_poster = Image.open(io.BytesIO(anime["imagem"]))
            largura_caractere = 24
            proporcao = largura_caractere / imagem_poster.width
            nova_largura = largura_caractere
            nova_altura = int(imagem_poster.height * proporcao)
            imagem_poster = Pixels.from_image(
                imagem_poster, resize=(nova_largura, nova_altura)
            )
            poster = AnimePoster(imagem_poster, series=anime, classes="poster")
            nome = Label(nome.__str__(), classes="nome_anime")
            cartao = Vertical(poster, nome, classes="cartao-anime")
            painel_animes.mount(cartao)
            if i == 0:
                poster.add_class("selecionado")


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
