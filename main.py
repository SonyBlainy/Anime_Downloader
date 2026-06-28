import os


def configurar_diretorios():
    caminhos = {
        "animes": os.path.join(
            os.path.expandvars(r"%userprofile%"), "Desktop", "Animes"
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
from async_tkinter_loop import async_handler, async_mainloop
from async_tkinter_loop.mixins import AsyncCTk
import customtkinter as ctk
import logging
from PIL import Image
import io
import re
import pandas as pd
from shutil import rmtree


class CustomHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            os.startfile("log.log")
            sys.exit()


versao = "v1.2.5"
from nucleo import core


class AnimeDownloaderGUI(ctk.CTk, AsyncCTk):
    def __init__(self):
        super().__init__()
        self.title(f"Anime Downloader {versao}")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.animes = None
        self.after(10, lambda: self.state("zoomed"))
        self.after(0, lambda: asyncio.create_task(self.iniciar()))

    def tela_base(self, botao=True):
        botoes_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        icone_biblioteca = ctk.CTkImage(imagem_biblioteca, size=(24, 24))
        icone_pesquisar = ctk.CTkImage(imagem_pesquisar, size=(24, 24))
        icone_update = ctk.CTkImage(imagem_update, size=(24, 24))
        anime_texto = ctk.CTkLabel(
            self.main_frame, text="Anime Downloader", font=("Arial", 18, "bold")
        )
        linha_h = ctk.CTkFrame(self.main_frame, height=4, corner_radius=2)
        linha_v = ctk.CTkFrame(self.main_frame, width=4, corner_radius=2)
        if botao:
            pesquisa = ctk.CTkButton(
                botoes_frame,
                image=icone_pesquisar,
                compound="left",
                fg_color="transparent",
                text="Pesquisar",
                command=async_handler(self.pesquisar),
            )
            biblioteca = ctk.CTkButton(
                botoes_frame,
                image=icone_biblioteca,
                compound="left",
                fg_color="transparent",
                text="Biblioteca",
                command=self.menu_principal,
            )
            update = ctk.CTkButton(
                botoes_frame,
                image=icone_update,
                text="Update",
                fg_color="transparent",
                compound="left",
                command=async_handler(lambda: core.update(versao)),
            )
        else:
            pesquisa = ctk.CTkButton(
                botoes_frame,
                image=icone_pesquisar,
                compound="left",
                fg_color="transparent",
                text="Pesquisar",
                command=None,
            )
            biblioteca = ctk.CTkButton(
                botoes_frame,
                image=icone_biblioteca,
                compound="left",
                fg_color="transparent",
                text="Biblioteca",
                command=None,
            )
            update = ctk.CTkButton(
                botoes_frame,
                image=icone_update,
                text="Update",
                fg_color="transparent",
                compound="left",
                command=None,
            )
        anime_texto.pack(pady=20, anchor="w")
        linha_h.pack(fill="x")
        botoes_frame.pack(side="left", anchor="nw")
        pesquisa.pack(pady=5, anchor="nw")
        biblioteca.pack(pady=5, anchor="nw")
        update.pack(pady=5, anchor="nw")
        linha_v.pack(fill="y", padx=5, side="left", anchor="nw")

    def deletar_e_atualizar(self, anime):
        self.animes = core.deletar_anime(anime, self.animes)
        self.menu_principal()

    async def iniciar(self):
        self.clear_frame()
        self.tela_base()
        frame_log = ctk.CTkFrame(self.main_frame)
        frame_log.pack(fill="both", expand=True)
        if not os.path.exists("dados.parquet"):
            core.label_log(frame_log, "Arquivo de dados não existe").pack(
                anchor="nw", pady=5, padx=5
            )
            await asyncio.sleep(1)
            core.label_log(frame_log, "Gerando arquivo...").pack(
                anchor="nw", padx=5, pady=5
            )
            await asyncio.sleep(1)
            self.animes = core.dataset()
            self.animes = await core.verificar_animes(self.animes, True)
        else:
            core.label_log(frame_log, "Carregando dados do arquivo...").pack(
                anchor="nw", padx=5, pady=5
            )
            await asyncio.sleep(1)
            with open("dados.parquet", "rb") as arquivo:
                self.animes = pd.read_parquet(arquivo)
            self.animes = await core.verificar_animes(self.animes)
        self.animes.sort_index(inplace=True)
        self.menu_principal()

    async def anime_exibir(self, anime, anime_poster):
        self.clear_frame()
        self.tela_base()
        estacoes = {
            "Spring": "Primavera",
            "Summer": "Verão",
            "Autumn": "Outono",
            "Fall": "Outono",
            "Winter": "Inverno",
        }
        anime_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        anime_nome = ctk.CTkLabel(
            anime_frame, text=anime["nome_pesquisa"], font=("Arial", 18, "bold")
        )
        anime_nome.pack(pady=5, padx=5, anchor="nw")
        info_frame_sup = ctk.CTkFrame(anime_frame)
        info_frame_sup.pack(fill="x", anchor="nw")
        anime_poster = ctk.CTkLabel(
            info_frame_sup, text=None, image=anime_poster, compound="top"
        )
        anime_poster.pack(pady=5, padx=5, anchor="nw", side="left")
        info_anime = ctk.CTkFrame(info_frame_sup, fg_color="transparent")
        info_anime.pack(padx=2, pady=5, anchor="nw", fill="x")
        info_frame_infi = ctk.CTkFrame(anime_frame)
        botao_frame = ctk.CTkFrame(info_frame_sup, fg_color="transparent")
        botao_frame.pack(padx=2, pady=5, fill="x")
        botao_download = ctk.CTkButton(
            botao_frame,
            text="Download",
            command=lambda: asyncio.create_task(self.download_anime(anime)),
        )
        botao_download.pack(padx=2, anchor="nw", side="left")
        if "caminho" in anime.keys():
            botao_listar_ep = ctk.CTkButton(
                botao_frame,
                text="Listar Episódios",
                command=lambda: self.listar_ep(anime),
            )
            botao_listar_ep.pack(padx=10, anchor="nw", side="left")
            pasta = ctk.CTkButton(
                botao_frame,
                text="Abrir pasta",
                command=lambda: core.abrir_pasta(anime["caminho"]),
            )
            pasta.pack(padx=2, anchor="nw", side="left")
            deletar = ctk.CTkButton(
                botao_frame,
                text="Excluir anime",
                command=lambda: self.deletar_e_atualizar(anime),
            )
            deletar.pack(padx=10, anchor="nw", side="left")
        data = datetime.strptime(anime["info"]["start_date"], "%Y-%m-%d")
        data = data.strftime("%d/%m/%Y")
        data = ctk.CTkLabel(
            info_anime, text=f"Data de lançamento: {data}", font=("Arial", 13)
        )
        nota = ctk.CTkLabel(
            info_anime, text=f"Nota: {anime['info']['mean']}", font=("Arial", 13)
        )
        genero = ctk.CTkLabel(
            info_anime, text="Genero: " + ", ".join(anime["info"]["genres"])
        )
        status = ctk.CTkLabel(info_anime, text=f"Status: {anime['info']['status']}")
        n_eps = ctk.CTkLabel(
            info_anime, text=f"Números de Episódios: {anime['info']['num_episodes']}"
        )
        if anime["info"]["broadcast"]:
            dia_lancamento = ctk.CTkLabel(
                info_anime,
                text=f"Hora de exibição: {anime['info']['broadcast']['dia']} as {anime['info']['broadcast']['hora']}",
            )
        else:
            dia_lancamento = None
        season = ctk.CTkLabel(
            info_anime,
            text=f"Season: {estacoes[anime['info']['start_season']['season'].capitalize()]} de {anime['info']['start_season']['year']}",
        )
        fonte = ctk.CTkLabel(
            info_anime, text=f"Fonte: {anime['info']['source'].capitalize()}"
        )
        nota.pack(pady=2, padx=5, anchor="nw")
        genero.pack(pady=2, padx=5, anchor="nw")
        data.pack(pady=2, padx=5, anchor="nw")
        if dia_lancamento:
            dia_lancamento.pack(pady=2, padx=5, anchor="nw")
        fonte.pack(pady=2, padx=5, anchor="nw")
        season.pack(pady=2, padx=5, anchor="nw")
        status.pack(pady=2, padx=5, anchor="nw")
        n_eps.pack(pady=2, padx=5, anchor="nw")
        info_frame_infi.pack(pady=5, padx=5, anchor="nw", fill="both", expand=True)
        sinopse = ctk.CTkLabel(
            info_frame_infi,
            text=f"Sinopse: {anime['info']['synopsis']}",
            font=("Arial", 14),
            wraplength=1175,
        )
        sinopse.pack(pady=5, padx=5, anchor="nw")
        anime_frame.pack(expand=True, fill="both", side="left")

    async def download_anime(self, anime):
        self.clear_frame()
        self.tela_base()
        marcar_todos = False
        anime = await core.selecionar_ep(anime)
        if "caminho" in anime.keys():
            with os.scandir(anime["caminho"]) as i:
                if (
                    anime["info"]["num_episodes"] == len(os.listdir(anime["caminho"]))
                    and anime["info"]["num_episodes"] != 0
                ):
                    marcar_todos = True
                try:
                    eps_baixados = [
                        re.search(r"- (\w{2,4}) \[1080p", ep.name).group(1) for ep in i
                    ]
                except Exception as e:
                    logging.exception(
                        f"Erro {e} ao obter lista de eps baixados, de um dos seguintes arquivos: {[ep.name for ep in os.scandir(anime['caminho'])]}"
                    )
                    eps_baixados = []
        else:
            eps_baixados = []
        frame_principal = ctk.CTkFrame(self.main_frame)
        frame_principal.pack(pady=5, padx=5, fill="both", expand=True, anchor="nw")
        frame_anime = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_anime.pack(padx=5, pady=5, anchor="nw", fill="x")
        anime_nome = ctk.CTkLabel(
            frame_anime,
            text=anime["nome_pesquisa"],
            fg_color="transparent",
            font=("Arial", 20, "bold"),
        )
        anime_nome.pack(anchor="nw", side="left")
        n_eps = ctk.CTkLabel(
            frame_anime,
            text=f"{len(anime['ep'])} Episódios",
            font=("Arial", 20, "bold"),
        )
        n_eps.pack(anchor="ne")
        frame_eps = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_eps.pack(padx=5, pady=5, anchor="nw", side="left")
        frame_direita = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_direita.pack(anchor="ne")
        botao_download = ctk.CTkButton(
            frame_direita,
            text="Baixar eps selecionados",
            command=lambda: asyncio.create_task(
                self.baixar_eps(frame_eps, anime, eps_baixados)
            ),
        )
        botao_download.pack(pady=5, anchor="nw")
        botao_tudo = ctk.CTkButton(
            frame_direita,
            text="Baixar todos os eps disponiveis",
            command=lambda: asyncio.create_task(self.baixar_tudo(anime, eps_baixados)),
        )
        botao_tudo.pack(pady=5, anchor="nw")
        frame_linha = ctk.CTkFrame(frame_eps, fg_color="transparent")
        frame_linha.pack(pady=5, padx=5, anchor="nw")
        for i, ep in enumerate(anime["ep"]):
            botao_check = ctk.CTkCheckBox(
                frame_linha, text=ep["ep"], font=("Arial", 12)
            )
            botao_check.pack(pady=5, padx=5, anchor="nw", side="left")
            if ep["ep"].split()[1] in eps_baixados or marcar_todos:
                botao_check.select()
                botao_check.configure(state="disabled")
            if (i + 1) % 5 == 0 and i != 0 and i != len(anime.ep) - 1:
                frame_linha = ctk.CTkFrame(frame_eps, fg_color="transparent")
                frame_linha.pack(pady=5, padx=5, anchor="nw")

    async def downloads(self):
        self.clear_frame()
        self.tela_base()
        infos = await core.torrent_info()
        print(infos)
        frame_principal = ctk.CTkScrollableFrame(
            self.main_frame, fg_color="transparent"
        )
        frame_principal.pack(fill="both", expand=True)
        frame_nome = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_nome.pack(fill="x", anchor="nw", expand=True)
        n_anime = ctk.CTkLabel(
            frame_nome,
            text=f"{len(infos.keys())} animes encontrados",
            font=("Arial", 18, "bold"),
        )
        n_anime.pack(anchor="nw")
        for anime in infos.keys():
            anime_frame = ctk.CTkFrame(frame_principal, fg_color="transparent")
            anime_frame.pack(anchor="nw", fill="x", expand=True, pady=10)
            imagem = Image.open(io.BytesIO(infos[anime]["anime"].imagem))
            tamanho = (imagem.width // 3, imagem.height // 3)
            imagem = ctk.CTkImage(imagem, size=tamanho)
            imagem_poster = ctk.CTkLabel(anime_frame, text=None, image=imagem)
            imagem_poster.pack(anchor="nw", side="left")

    async def baixar_eps(self, frame: ctk.CTkFrame, anime: pd.Series, baixados):
        eps = []
        anime = core.criar_pasta(anime)
        for f in frame.winfo_children():
            for botao in f.winfo_children():
                if botao.get():
                    eps.append(botao.cget("text"))
        eps_baixar = [
            ep
            for ep in anime["ep"]
            if ep["ep"] in eps and ep["ep"].split()[1] not in baixados
        ]
        for ep in eps_baixar:
            ep["caminho"] = anime["caminho"]
        if anime["server"] == "Erai":
            eps_baixar = [core.baixar_ep_erai(ep) for ep in eps_baixar]
            await asyncio.gather(*eps_baixar)
        elif anime["server"] == "TopAnimes":
            self.clear_frame()
            self.tela_base(False)
            eps_baixar = [
                core.baixar_ep_top_animes(ep, self.main_frame) for ep in eps_baixar
            ]
            await asyncio.gather(*eps_baixar)
        elif anime["server"] == "Infinite":
            self.clear_frame()
            self.tela_base(False)
            eps_baixar = [
                core.baixar_ep_infinite(ep, self.main_frame) for ep in eps_baixar
            ]
            await asyncio.gather(*eps_baixar)
        self.animes = core.adicionar_anime(self.animes, anime)
        self.animes.sort_index(inplace=True)
        self.menu_principal()

    async def baixar_tudo(self, anime: pd.Series, baixados):
        anime = core.criar_pasta(anime)
        for ep in anime["ep"]:
            if ep["ep"].split()[1] not in baixados:
                ep["caminho"] = anime["caminho"]
        if anime["server"] == "Erai":
            eps = [
                core.baixar_ep_erai(ep) for ep in anime["ep"] if "caminho" in ep.keys()
            ]
            await asyncio.gather(*eps)
        elif anime["server"] == "TopAnimes":
            self.clear_frame()
            self.tela_base(False)
            eps = [
                core.baixar_ep_top_animes(ep, self.main_frame)
                for ep in anime["ep"]
                if "caminho" in ep.keys()
            ]
            await asyncio.gather(*eps)
        elif anime["server"] == "Infinite":
            self.clear_frame()
            self.tela_base(False)
            eps = [
                core.baixar_ep_infinite(ep, self.main_frame)
                for ep in anime["ep"]
                if "caminho" in ep.keys()
            ]
            await asyncio.gather(*eps)
        self.animes = core.adicionar_anime(self.animes, anime)
        self.animes.sort_index(inplace=True)
        self.menu_principal()

    def listar_ep(self, anime: pd.Series):
        arquivos = os.listdir(anime["caminho"])
        if arquivos:
            for d in os.scandir(anime["caminho"]):
                if os.path.isdir(d.path):
                    caminho = os.path.split(d.path)[0]
                    for a in os.scandir(d.path):
                        core.mover_arquivo(a.path, caminho)
                    rmtree(d.path)
                    arquivos = os.listdir(anime["caminho"])
                    break
                else:
                    break
            self.clear_frame()
            self.tela_base()
            n_eps_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            n_eps_frame.pack(padx=5, pady=5, anchor="nw", fill="x")
            n_eps = ctk.CTkLabel(
                n_eps_frame,
                text=f"{len(arquivos)} Episódios de {anime['nome_pesquisa']}",
                font=("Arial", 20, "bold"),
            )
            n_eps.pack(pady=5, anchor="nw")
            eps_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
            eps_frame.pack(pady=5, padx=5, fill="both", expand=True)
            linha = ctk.CTkFrame(eps_frame, fg_color="transparent")
            linha.pack(pady=5, fill="x", anchor="nw")
            frames = core.gerar_frames(anime)
            for i, ep in enumerate(os.scandir(anime["caminho"])):
                if i != 0 and i % 3 == 0:
                    linha = ctk.CTkFrame(eps_frame, fg_color="transparent")
                    linha.pack(pady=5, fill="x", anchor="nw")
                n_ep = str(re.search(r" - (\d{1,2})", ep.name).group(1))
                try:
                    imagem = ctk.CTkImage(frames[n_ep], size=(384, 216))
                except:
                    continue
                ep_poster = ctk.CTkLabel(
                    linha,
                    image=imagem,
                    text=ep.name,
                    font=("Arial", 15),
                    wraplength=390,
                    compound="top",
                    justify="center",
                )
                ep_poster.pack(padx=5, anchor="nw", side="left")
                ep_poster.bind("<Button-1>", lambda e, a=ep.path: os.startfile(a))

    async def pesquisar_anime(self, nome):
        self.clear_frame()
        self.tela_base()
        animes = await core.pesquisar(nome)
        animes_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        animes_frame.pack(pady=5, fill="both", expand=True, side="left", anchor="nw")
        n_frame = ctk.CTkFrame(animes_frame, fg_color="transparent")
        n_frame.pack(pady=5, fill="x")
        n_label = ctk.CTkLabel(
            n_frame, text=f"{len(animes)} Animes", font=("Arial", 18, "bold")
        )
        n_label.pack(anchor="ne")

        def animes_listar(animes_lista: list):
            if not animes_lista:
                frame_p = ctk.CTkFrame(animes_frame, fg_color="transparent")
                frame_p.pack(anchor="nw", expand=True)
                label = ctk.CTkLabel(
                    frame_p, text=f"Nenhum anime encontrado", font=("Arial", 18, "bold")
                )
                label.pack()
                return
            frame_nome = ctk.CTkFrame(animes_frame, fg_color="transparent")
            frame_nome.pack(anchor="nw", fill="x", pady=10)
            nome = ctk.CTkLabel(
                frame_nome, text=animes_lista[0]["server"], font=("Arial", 20, "bold")
            )
            nome.pack(anchor="nw")
            frame_p = ctk.CTkFrame(animes_frame, fg_color="transparent")
            frame_p.pack(anchor="nw", expand=True)
            linha = ctk.CTkFrame(frame_p, fg_color="transparent")
            linha.pack(anchor="nw", fill="x", pady=5)
            for i, anime in enumerate(animes_lista):
                if i != 0 and i % 5 == 0:
                    linha = ctk.CTkFrame(frame_p, fg_color="transparent")
                    linha.pack(anchor="nw", fill="x", pady=5)
                try:
                    imagem = Image.open(io.BytesIO(anime["imagem"]))
                except:
                    logging.warning(f"Erro ao carregar imagem do anime {anime.name}")
                    continue
                comprimento = imagem.width // 2
                tamanho = (comprimento, imagem.height // 2)
                imagem_poster = ctk.CTkImage(imagem, size=tamanho)
                anime_poster = ctk.CTkLabel(
                    linha,
                    text=anime.name,
                    image=imagem_poster,
                    compound="top",
                    font=("Arial", 14),
                    wraplength=comprimento,
                )
                anime_poster.pack(anchor="nw", side="left", padx=8)
                anime_poster.bind(
                    "<Button-1>",
                    lambda e, a=anime, i=imagem_poster: asyncio.create_task(
                        self.anime_exibir(a, i)
                    ),
                )

        erai = [a for a in animes if a["server"] == "Erai"]
        topanimes = [a for a in animes if a["server"] == "TopAnimes"]
        infinite = [a for a in animes if a["server"] == "Infinite"]
        animes_listar(erai)
        animes_listar(topanimes)
        animes_listar(infinite)

    async def pesquisar(self):
        self.clear_frame()
        self.tela_base()
        barra_pesquisa = ctk.CTkEntry(
            self.main_frame,
            width=200,
            height=30,
            placeholder_text="Digite o nome do anime...",
            corner_radius=20,
            fg_color="#FFFFFF",
            text_color="#000000",
            border_width=1,
        )
        barra_pesquisa.pack(pady=20)
        barra_pesquisa.bind(
            "<Return>",
            lambda e: asyncio.create_task(self.pesquisar_anime(barra_pesquisa.get())),
        )
        barra_pesquisa.focus()

    def clear_frame(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

    def menu_principal(self):
        self.clear_frame()
        self.tela_base()
        if len(self.animes):
            n_animes_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            n_animes_frame.pack(fill="x", pady=5)
            n_animes = ctk.CTkLabel(
                n_animes_frame,
                text=f"{len(self.animes)} Animes",
                font=("Arial", 20, "bold"),
            )
            n_animes.pack(anchor="nw")
            if len(self.animes) > 5:
                animes_frame = ctk.CTkScrollableFrame(
                    self.main_frame, fg_color="transparent"
                )
            else:
                animes_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            animes_frame.pack(fill="both", pady=5, expand=True)
            linha = ctk.CTkFrame(animes_frame, fg_color="transparent")
            linha.pack(pady=5, padx=5, fill="x", anchor="nw")
            self.animes = self.animes[
                self.animes["caminho"].apply(lambda caminho: os.path.exists(caminho))
            ]
            for i, anime in enumerate(self.animes.index):
                anime = self.animes.loc[anime]
                imagem = Image.open(io.BytesIO(anime.imagem))
                comprimento = imagem.width // 2
                tamanho = (comprimento, imagem.height // 2)
                imagem_poster = ctk.CTkImage(imagem, size=tamanho)
                poster = ctk.CTkLabel(
                    linha,
                    image=imagem_poster,
                    text=anime.name,
                    font=("Arial", 14),
                    compound="top",
                    wraplength=comprimento + 10,
                    justify="center",
                )
                poster.pack(pady=5, padx=5, anchor="nw", side="left")
                poster.bind(
                    "<Button-1>",
                    lambda event, a=anime, i=imagem_poster: asyncio.create_task(
                        self.anime_exibir(a, i)
                    ),
                )
                if i % 4 == 0 and i != 0 and i != len(self.animes) - 1:
                    linha = ctk.CTkFrame(animes_frame, fg_color="transparent")
                    linha.pack(pady=5, padx=5, fill="x", anchor="nw")


if __name__ == "__main__":
    freeze_support()
    global path
    path = os.getenv("caminho")
    logging.basicConfig(
        filename="log.log",
        filemode="w",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    imagem_pesquisar = Image.open("icones\\search.png")
    imagem_biblioteca = Image.open("icones\\home.png")
    imagem_update = Image.open("icones\\update.png")
    logger = logging.getLogger()
    logger.addHandler(CustomHandler())
    core.verificar_navegador()
    core.verificar_ffmpeg()
    asyncio.run(core.verifica_cookies())
    app = AnimeDownloaderGUI()
    async_mainloop(app)
