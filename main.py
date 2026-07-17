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
from textual.screen import Screen
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


class AnimeInfo(Screen):
    BINDINGS = [("escape", "sair", "Voltar"), ("d", "download", "Download")]

    def __init__(
        self,
        series: pd.Series,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.anime_series = series

    def compose(self) -> ComposeResult:
        imagem_poster = Image.open(io.BytesIO(self.anime_series["imagem"]))
        largura_caractere = 45
        proporcao = largura_caractere / imagem_poster.width
        nova_largura = largura_caractere
        nova_altura = int(imagem_poster.height * proporcao)
        imagem_poster = Pixels.from_image(
            imagem_poster, resize=(nova_largura, nova_altura)
        )
        nome = self.anime_series.name
        infos = self.anime_series["info"]
        yield Header()
        yield Footer()
        with Container(id="anime_info_frame"):
            yield Static(imagem_poster, classes="poster")
            with Container(id="infos_anime"):
                with Container(id="anime_nome_frame"):
                    yield Label(nome.__str__().strip(), id="nome_anime")
                with Container(id="infos_frame"):
                    yield Label(f"Nota: {infos['mean']}", id="anime_nota")
                    yield Label(f"Episódios: {infos['num_episodes']}", id="n_eps")
                    yield Label(f"Status: {infos['status']}", id="status")
                    yield Label(f"Fonte: {infos['source']}", id="fonte")
                    yield Label(
                        f"Season: {infos['start_season']['season'].upper()}",
                        id="season",
                    )
                    yield Label(
                        f"Lançamento: {infos['broadcast']['dia']} as {infos['broadcast']['hora']}",
                        id="lancamento",
                    )
                yield Label("Genêros: " + ", ".join(infos["genres"]), id="generos")
                with Container(id="sinopse_frame"):
                    yield Label(f"Sinopse:\n{infos['synopsis']}", id="sinopse")

    def action_sair(self):
        self.app.pop_screen()


class AnimePesquisa(Screen):
    BINDINGS = [("escape", "cancelar", "Cancelar")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Input(placeholder="Digite o nome do anime...", id="pesquisa")

    def on_mount(self):
        self.query_one(Input).focus()

    @on(Input.Submitted)
    def enviar(self, evento: Input.Submitted):
        self.dismiss(evento.value)

    def action_cancelar(self):
        self.dismiss()


class AnimeExibirPesquisa(Screen):
    BINDINGS = [
        Binding("right", "direita", show=False),
        Binding("left", "esquerda", show=False),
        Binding("up", "cima", show=False),
        Binding("down", "baixo", show=False),
        Binding("enter", "enter", show=False),
        Binding("escape", "voltar", "Voltar"),
    ]

    def __init__(
        self,
        animes: pd.DataFrame,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.animes = animes

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Horizontal(classes="n_animes_frame"):
            yield Label(f"{len(self.animes)} animes encontrados", classes="n_animes")
        with Container(classes="painel_animes"):
            for n, (nome, anime) in enumerate(self.animes.iterrows()):
                imagem_poster = Image.open(io.BytesIO(anime["imagem"]))
                largura_caractere = 24
                proporcao = largura_caractere / imagem_poster.width
                nova_largura = largura_caractere
                nova_altura = int(imagem_poster.height * proporcao)
                imagem_poster = Pixels.from_image(
                    imagem_poster, resize=(nova_largura, nova_altura)
                )
                with Vertical(classes="cartao-anime"):
                    poster = AnimePoster(imagem_poster, anime, classes="poster")
                    yield poster
                    yield Label(nome.__str__(), classes="nome_anime")
                    if n == 0:
                        poster.add_class("selecionado")

    def action_voltar(self):
        self.app.pop_screen()

    def action_direita(self):
        posters = self.query(
            ".poster",
        )
        for i, p in enumerate(posters):
            if "selecionado" in p.classes:
                poster_selecionado = p
                n = i
                if n + 1 < len(posters):
                    poster_selecionado.remove_class("selecionado")
                    posters[n + 1].add_class("selecionado")
                    posters[n + 1].parent.scroll_visible()
                break

    def action_esquerda(self):
        posters = self.query(
            ".poster",
        )
        for i, p in enumerate(posters):
            if "selecionado" in p.classes:
                poster_selecionado = p
                n = i
                if n - 1 >= 0:
                    poster_selecionado.remove_class("selecionado")
                    posters[n - 1].add_class("selecionado")
                    posters[n - 1].parent.scroll_visible()
                break

    def action_cima(self):
        posters = self.query(
            ".poster",
        )
        for i, p in enumerate(posters):
            if "selecionado" in p.classes:
                poster_selecionado = p
                n = i
                if n - 5 >= 0:
                    poster_selecionado.remove_class("selecionado")
                    posters[n - 5].add_class("selecionado")
                    posters[n - 5].parent.scroll_visible()
                break

    def action_baixo(self):
        posters = self.query(
            ".poster",
        )
        for i, p in enumerate(posters):
            if "selecionado" in p.classes:
                poster_selecionado = p
                n = i
                if n + 5 < len(posters):
                    poster_selecionado.remove_class("selecionado")
                    posters[n + 5].add_class("selecionado")
                    posters[n + 5].parent.scroll_visible()
                break

    def action_enter(self):
        anime = self.query_one(".selecionado", AnimePoster)
        self.app.push_screen(AnimeInfo(series=anime.anime_series))


class LogPesquisa(Screen):
    def __init__(
        self,
        nome: str,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.nome_anime = nome

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield RichLog(id="frame_log")

    def on_mount(self):
        self.busca()

    @work
    async def busca(self):
        log_widget = self.query_one("#frame_log", RichLog)

        def salvar_log(texto: str):
            log_widget.write(texto)

        animes = await core.pesquisar(self.nome_anime, salvar_log)
        self.dismiss(animes)


class AnimeDownloaderTUI(App):
    CSS_PATH = "estilo.tcss"
    BINDINGS = [("q", "sair", "Sair")]
    ENABLE_COMMAND_PALETTE = False

    def on_mount(self):
        self.title = "Anime Downloader " + versao
        self.push_screen(MenuPrincipal())

    def action_sair(self):
        self.exit()


class MenuPrincipal(Screen):
    BINDINGS = [
        ("p", "pesquisa", "Pesquisar"),
        Binding("right", "direita", show=False),
        Binding("left", "esquerda", show=False),
        Binding("up", "cima", show=False),
        Binding("down", "baixo", show=False),
        Binding("enter", "enter", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield RichLog(id="frame_log")

    async def on_mount(self):
        self.carregar_dados()

    def action_direita(self):
        posters = self.query(
            ".poster",
        )
        for i, p in enumerate(posters):
            if "selecionado" in p.classes:
                poster_selecionado = p
                n = i
                if n + 1 < len(posters):
                    poster_selecionado.remove_class("selecionado")
                    posters[n + 1].add_class("selecionado")
                    posters[n + 1].parent.scroll_visible()
                break

    def action_esquerda(self):
        posters = self.query(
            ".poster",
        )
        for i, p in enumerate(posters):
            if "selecionado" in p.classes:
                poster_selecionado = p
                n = i
                if n - 1 >= 0:
                    poster_selecionado.remove_class("selecionado")
                    posters[n - 1].add_class("selecionado")
                    posters[n - 1].parent.scroll_visible()
                break

    def action_cima(self):
        posters = self.query(
            ".poster",
        )
        for i, p in enumerate(posters):
            if "selecionado" in p.classes:
                poster_selecionado = p
                n = i
                if n - 5 >= 0:
                    poster_selecionado.remove_class("selecionado")
                    posters[n - 5].add_class("selecionado")
                    posters[n - 5].parent.scroll_visible()
                break

    def action_baixo(self):
        posters = self.query(
            ".poster",
        )
        for i, p in enumerate(posters):
            if "selecionado" in p.classes:
                poster_selecionado = p
                n = i
                if n + 5 < len(posters):
                    poster_selecionado.remove_class("selecionado")
                    posters[n + 5].add_class("selecionado")
                    posters[n + 5].parent.scroll_visible()
                break

    def action_enter(self):
        anime = self.query_one(".selecionado", AnimePoster)
        self.app.push_screen(AnimeInfo(series=anime.anime_series))

    @work
    async def action_pesquisa(self):
        nome = await self.app.push_screen_wait(AnimePesquisa())
        if nome:
            animes = await self.app.push_screen_wait(LogPesquisa(nome))
            self.app.push_screen(AnimeExibirPesquisa(animes))

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

    async def exibir_animes(self, animes=pd.DataFrame(), pesquisa=False):
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
