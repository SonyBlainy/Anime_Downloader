import os
from dotenv import load_dotenv

load_dotenv()
from nucleo import core
from multiprocessing import freeze_support
import asyncio
import logging
from PIL import Image
import io
import re
import pandas as pd
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Label, RichLog, Static, Input
from textual.widget import Widget
from textual.containers import Vertical, Container, Horizontal
from textual.css.query import DOMQuery
from textual import work, on
from textual.binding import Binding
from textual.screen import Screen
from rich_pixels import Pixels


versao = "v1.3"


class AnimePoster(Static):
    def __init__(self, renderizavel, series: pd.Series, *args, **kwars) -> None:
        super().__init__(renderizavel, *args, **kwars)
        self.anime_series = series


class Episodio(Label):
    def __init__(self, content, caminho: str, *args, **kwargs) -> None:
        super().__init__(content, *args, **kwargs)
        self.caminho = caminho


def navegacao(
    acao: str, quantidade: int, query: DOMQuery[Widget], tipo: str = "assistir"
):
    def direita():
        if tipo == "download":
            eps_baixados = [ep for ep in query if ep.has_class("selecionado")]
            if len(eps_baixados) > 1:
                for ep in eps_baixados[:-1]:
                    ep.remove_class("selecionado")
            for n, ep in enumerate(query):
                if ep.has_class("selecionado"):
                    if n == len(query) - 1:
                        break
                    elif not query[n + 1].has_class("baixado"):
                        ep.remove_class("selecionado")
                        query[n + 1].add_class("selecionado")
                    else:
                        for ep2 in query[n + 1 :]:
                            if not ep2.has_class("baixado"):
                                ep.remove_class("selecionado")
                                ep2.add_class("selecionado")
                                break
                    break
        else:
            for n, ep in enumerate(query):
                if ep.has_class("selecionado") and n + 1 < len(query):
                    ep.remove_class("selecionado")
                    query[n + 1].add_class("selecionado")
                    if tipo == "anime":
                        query[n + 1].parent.scroll_visible()
                    break

    def esquerda():
        if tipo == "download":
            eps_baixados = [ep for ep in query if ep.has_class("selecionado")]
            if len(eps_baixados) > 1:
                for ep in eps_baixados[1:]:
                    ep.remove_class("selecionado")
            for n, ep in enumerate(query):
                if ep.has_class("selecionado"):
                    if n == 0:
                        break
                    elif not query[n - 1].has_class("baixado"):
                        ep.remove_class("selecionado")
                        query[n - 1].add_class("selecionado")
                    else:
                        for ep2 in query[n - 1 :: -1]:
                            if not ep2.has_class("baixado"):
                                ep.remove_class("selecionado")
                                ep2.add_class("selecionado")
                                break
                    break
        else:
            for n, ep in enumerate(query):
                if ep.has_class("selecionado") and n - 1 >= 0:
                    ep.remove_class("selecionado")
                    query[n - 1].add_class("selecionado")
                    if tipo == "anime":
                        query[n - 1].parent.scroll_visible()
                    break

    def cima():
        if tipo == "download":
            eps_baixados = [ep for ep in query if ep.has_class("selecionado")]
            if len(eps_baixados) > 1:
                for ep in eps_baixados[1::-1]:
                    ep.remove_class("selecionado")
            for n, ep in enumerate(query):
                if ep.has_class("selecionado"):
                    if n == 0:
                        break
                    elif n - quantidade >= 0:
                        if not query[n - quantidade].has_class("baixado"):
                            ep.remove_class("selecionado")
                            query[n - quantidade].add_class("selecionado")
                        else:
                            for ep2 in query[n - quantidade + 1 : n]:
                                if not ep2.has_class("baixado"):
                                    ep.remove_class("selecionado")
                                    ep2.add_class("selecionado")
                                    break
                    else:
                        if not query[0].has_class("baixado"):
                            ep.remove_class("selecionado")
                            query[0].add_class("selecionado")
                        else:
                            for ep2 in query[1:n]:
                                if not ep2.has_class("baixado"):
                                    ep.remove_class("selecionado")
                                    ep2.add_class("selecionado")
                                    break
                    break
        else:
            for n, ep in enumerate(query):
                if ep.has_class("selecionado"):
                    ep.remove_class("selecionado")
                    if n - quantidade >= 0:
                        query[n - quantidade].add_class("selecionado")
                        if tipo == "anime":
                            query[n - quantidade].parent.scroll_visible()
                    else:
                        query[0].add_class("selecionado")
                        if tipo == "anime":
                            query[0].parent.scroll_visible()
                    break

    def baixo():
        if tipo == "download":
            eps_baixados = [ep for ep in query if ep.has_class("selecionado")]
            if len(eps_baixados) > 1:
                for ep in eps_baixados[:-1]:
                    ep.remove_class("selecionado")
            for n, ep in enumerate(query):
                if ep.has_class("selecionado"):
                    if n == len(query) - 1:
                        break
                    elif n + quantidade < len(query):
                        if not query[n + quantidade].has_class("baixado"):
                            ep.remove_class("selecionado")
                            query[n + quantidade].add_class("selecionado")
                        else:
                            for ep2 in query[n + quantidade : n : -1]:
                                if not ep2.has_class("baixado"):
                                    ep.remove_class("selecionado")
                                    ep2.add_class("selecionado")
                                    break
                    else:
                        if not query[-1].has_class("baixado"):
                            ep.remove_class("selecionado")
                            query[-1].add_class("selecionado")
                        else:
                            for ep2 in query[:n:-1]:
                                if not ep2.has_class("baixado"):
                                    ep.remove_class("selecionado")
                                    ep2.add_class("selecionado")
                                    break
                    break
        else:
            for n, ep in enumerate(query):
                if ep.has_class("selecionado"):
                    ep.remove_class("selecionado")
                    if n + quantidade < len(query):
                        query[n + quantidade].add_class("selecionado")
                        if tipo == "anime":
                            query[n + quantidade].parent.scroll_visible()
                    else:
                        query[-1].add_class("selecionado")
                        if tipo == "anime":
                            query[-1].parent.scroll_visible()
                    break

    def shift_direita():
        eps_baixados = [n for n, ep in enumerate(query) if ep.has_class("selecionado")]
        n = eps_baixados[-1] + 1
        if n < len(query):
            if not query[n].has_class("baixado"):
                query[n].add_class("selecionado")
            else:
                for ep in query[n:]:
                    if not ep.has_class("baixado"):
                        ep.add_class("selecionado")
                        break

    def shift_esquerda():
        eps_baixados = [n for n, ep in enumerate(query) if ep.has_class("selecionado")]
        n = eps_baixados[0] - 1
        if n >= 0:
            if not query[n].has_class("baixado"):
                query[n].add_class("selecionado")
            else:
                for ep in query[n::-1]:
                    if not ep.has_class("baixado"):
                        ep.add_class("selecionado")
                        break

    def shift_cima():
        eps_baixados = [n for n, ep in enumerate(query) if ep.has_class("selecionado")]
        n = eps_baixados[0] - quantidade
        if n >= 0:
            for ep in query[eps_baixados[0] : n - 1 : -1]:
                if not ep.has_class("baixado"):
                    ep.add_class("selecionado")

    def shift_baixo():
        eps_baixados = [n for n, ep in enumerate(query) if ep.has_class("selecionado")]
        n = eps_baixados[-1] + quantidade
        if n < len(query):
            for ep in query[eps_baixados[-1] - 1 : n + 1]:
                if not ep.has_class("baixado"):
                    ep.add_class("selecionado")

    escolha = {
        "direita": lambda: direita(),
        "esquerda": lambda: esquerda(),
        "cima": lambda: cima(),
        "baixo": lambda: baixo(),
        "shift_direita": lambda: shift_direita(),
        "shift_esquerda": lambda: shift_esquerda(),
        "shift_cima": lambda: shift_cima(),
        "shift_baixo": lambda: shift_baixo(),
    }
    try:
        escolha[acao]()
    except Exception:
        pass


class AnimeInfo(Screen):
    BINDINGS = [
        ("escape", "sair", "Voltar"),
        ("d", "download", "Download"),
        ("r", "deletar", "Excluir anime"),
        ("a", "abrir", "Abrir pasta do anime"),
        ("l", "listar", "Listar Episodios"),
    ]

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
                    yield Label(f"Fonte: {infos['source'].capitalize()}", id="fonte")
                    yield Label(
                        f"Season: {infos['start_season']['season'].capitalize()}",
                        id="season",
                    )
                    if infos["broadcast"].get("dia"):
                        yield Label(
                            f"Lançamento: {infos['broadcast']['dia']} as {infos['broadcast']['hora']}",
                            id="lancamento",
                        )
                    yield Label(
                        f"Data de Lançamento: {infos['start_date']}",
                        id="data_lancamento",
                    )
                    yield Label("Studios: " + ", ".join(infos["studios"]), id="studios")
                yield Label("Genêros: " + ", ".join(infos["genres"]), id="generos")
                with Container(id="sinopse_frame"):
                    yield Label(f"Sinopse:\n{infos['synopsis']}", id="sinopse")

    @work
    async def action_download(self):
        anime = await core.selecionar_ep(self.anime_series)
        nomes = []
        try:
            eps_baixados = os.listdir(anime["caminho"])
        except Exception:
            pass
        else:
            for ep in eps_baixados:
                ep = re.search(r"- ([^-]*) \[1080p|- (\d*)\.", ep)
                nomes.append([a for a in ep.groups() if a][0])
        self.app.push_screen(AnimeDownload(anime, nomes))

    def action_deletar(self):
        if self.anime_series.get("caminho"):
            dados = self.app.screen_stack[1].animes
            core.deletar_anime(self.anime_series, dados)
            self.app.push_screen(MenuPrincipal())

    def action_listar(self):
        if self.anime_series.get("caminho"):
            self.app.push_screen(AnimeEpExibir(self.anime_series["caminho"]))

    def action_abrir(self):
        if self.anime_series.get("caminho"):
            core.abrir_pasta(self.anime_series["caminho"])

    def action_sair(self):
        self.app.pop_screen()


class AnimeEpExibir(Screen):
    BINDINGS = [
        Binding("escape", "voltar", show=False),
        Binding("enter", "exibir", "Abrir Ep"),
        Binding("up", "cima", show=False),
        Binding("down", "baixo", show=False),
        Binding("left", "esquerda", show=False),
        Binding("right", "direita", show=False),
    ]

    def __init__(
        self,
        caminho: str,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.caminho = caminho

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        for n, d in enumerate(os.scandir(self.caminho)):
            nome = re.search(r"- ([^-]*) \[1080|- (\d*)\.", d.name)
            nome = [a for a in nome.groups() if a][0]
            nome = Episodio("Episodio " + nome, d.path, classes="anime_nome")
            yield nome
            if n == 0:
                nome.add_class("selecionado")

    def action_direita(self):
        eps = self.query(".anime_nome")
        navegacao("direita", 6, eps)

    def action_esquerda(self):
        eps = self.query(".anime_nome")
        navegacao("esquerda", 6, eps)

    def action_cima(self):
        eps = self.query(".anime_nome")
        navegacao("cima", 6, eps)

    def action_baixo(self):
        eps = self.query(".anime_nome")
        navegacao("baixo", 6, eps)

    def action_exibir(self):
        ep = self.query_one(".selecionado", Episodio)
        os.startfile(ep.caminho)

    def action_voltar(self):
        self.app.pop_screen()


class AnimeDownload(Screen):
    BINDINGS = [
        Binding("escape", "voltar", show=False),
        Binding("enter", "baixar", "Baixar"),
        Binding("up", "cima", show=False),
        Binding("down", "baixo", show=False),
        Binding("left", "esquerda", show=False),
        Binding("right", "direita", show=False),
        Binding("shift+up", "shift_cima", show=False),
        Binding("shift+down", "shift_baixo", show=False),
        Binding("shift+left", "shift_esquerda", show=False),
        Binding("shift+right", "shift_direita", show=False),
    ]

    def __init__(
        self,
        anime: pd.Series,
        eps_baixados: list[str],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.anime = anime
        self.eps_baixados = eps_baixados

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        selecionado = False
        for ep in self.anime["ep"].copy():
            ep_nome = re.search(r"Episodio (.*)$", ep["ep"]).group(1)
            nome = Label(ep["ep"], classes="anime_nome")
            yield nome
            if ep_nome in self.eps_baixados:
                nome.add_class("baixado")
            if not selecionado:
                if not nome.has_class("baixado"):
                    nome.add_class("selecionado")
                    selecionado = True

    def action_direita(self):
        eps = self.query(".anime_nome")
        navegacao("direita", 6, eps, "download")

    def action_shift_direita(self):
        eps = self.query(".anime_nome")
        navegacao("shift_direita", 6, eps, "download")

    def action_esquerda(self):
        eps = self.query(".anime_nome")
        navegacao("esquerda", 6, eps, "download")

    def action_shift_esquerda(self):
        eps = self.query(".anime_nome")
        navegacao("shift_esquerda", 6, eps, "download")

    def action_cima(self):
        eps = self.query(".anime_nome")
        navegacao("cima", 6, eps, "download")

    def action_shift_cima(self):
        eps = self.query(".anime_nome")
        navegacao("shift_cima", 6, eps, "download")

    def action_baixo(self):
        eps = self.query(".anime_nome")
        navegacao("baixo", 6, eps, "download")

    def action_shift_baixo(self):
        eps = self.query(".anime_nome")
        navegacao("shift_baixo", 6, eps, "download")

    async def action_baixar(self):
        ep_s = self.query(".selecionado")
        eps_s = [ep.content for ep in ep_s]
        self.anime = core.criar_pasta(self.anime)
        if self.anime["server"] == "Erai":
            baixar = []
            for ep in self.anime["ep"]:
                if ep["ep"] in eps_s:
                    ep["caminho"] = self.anime["caminho"]
                    baixar.append(core.baixar_ep_erai(ep))
            await asyncio.gather(*baixar)
            menu = self.app.screen_stack[1]
            dados = menu.animes
            core.adicionar_anime(dados, self.anime)
            while len(self.app.screen_stack) > 1:
                self.app.pop_screen()
            self.app.push_screen(MenuPrincipal())
        elif self.anime["server"] in ["TopAnimes", "Infinite"]:
            eps = []
            for ep in self.anime["ep"]:
                if ep["ep"] in eps_s:
                    ep["caminho"] = self.anime["caminho"]
                    eps.append(ep)
            self.app.push_screen(AnimeBarraDownload(eps, self.anime))

    def action_voltar(self):
        self.dismiss()


class AnimeBarraDownload(Screen):
    def __init__(
        self,
        eps: list[dict],
        anime: pd.Series,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.eps = eps
        self.anime = anime

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(id="barra_download_caixa")

    def on_mount(self):
        self.baixar(self.eps)

    @work
    async def baixar(self, eps: list[dict]):
        caixa = self.query_one(Container)
        downloads = []
        for ep in eps:
            downloads.append(core.baixar(ep, caixa))
        await asyncio.gather(*downloads)
        menu = self.app.screen_stack[1]
        dados = menu.animes
        core.adicionar_anime(dados, self.anime)
        while len(self.app.screen_stack) > 1:
            self.app.pop_screen()
        self.app.push_screen(MenuPrincipal())


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
        posters = self.query(".poster")
        navegacao("direita", 5, posters, "anime")

    def action_esquerda(self):
        posters = self.query(".poster")
        navegacao("esquerda", 5, posters, "anime")

    def action_cima(self):
        posters = self.query(".poster")
        navegacao("cima", 5, posters, "anime")

    def action_baixo(self):
        posters = self.query(".poster")
        navegacao("baixo", 5, posters, "anime")

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

    def on_mount(self):
        self.carregar_dados()

    def action_direita(self):
        posters = self.query(".poster")
        navegacao('direita', 5, posters, 'anime')

    def action_esquerda(self):
        posters = self.query(".poster")
        navegacao('esquerda', 5, posters, 'anime')

    def action_cima(self):
        posters = self.query(".poster")
        navegacao('cima', 5, posters, 'anime')

    def action_baixo(self):
        posters = self.query(".poster")
        navegacao('baixo', 5, posters, 'anime')

    def action_enter(self):
        anime = self.query_one(".selecionado", AnimePoster)
        self.app.push_screen(AnimeInfo(series=anime.anime_series))

    @work
    async def action_pesquisa(self):
        nome = await self.app.push_screen_wait(AnimePesquisa())
        if nome:
            animes = await self.app.push_screen_wait(LogPesquisa(nome))
            self.app.push_screen(AnimeExibirPesquisa(animes))

    def carregar_dados(self):
        if os.path.exists("dados.parquet"):
            with open("dados.parquet", "rb") as arquivo:
                self.animes = pd.read_parquet(arquivo)
        else:
            self.animes = pd.DataFrame()
        self.animes = core.verificar_animes(self.animes)
        self.animes.sort_index(inplace=True)
        self.exibir_animes()

    def exibir_animes(self):
        n_animes_label = Label(f"{len(self.animes)} Animes", classes="n_animes")
        n_animes_container = Horizontal(n_animes_label, classes="n_animes_frame")
        self.mount(n_animes_container)
        painel_animes = Container(classes="painel_animes")
        self.mount(painel_animes)
        for i, (nome, anime) in enumerate(self.animes.iterrows()):
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
    core.verificar_navegador()
    asyncio.run(core.verifica_cookies())
    app = AnimeDownloaderTUI()
    app.run()
