from httpx import AsyncClient as Client
import navegador
import zipfile
import re
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from erai import erai_animes, torrent
from erai.erai_animes import ErroCookie
from topanimes import top_animes
from infinite import infinite
import logging
import os
import sys
import subprocess
import shutil
import asyncio
from customtkinter import CTkLabel, CTkFrame
import customtkinter as ctk
import pandas as pd
from deep_translator import GoogleTranslator as GT
from collections.abc import Callable

path = os.getenv("caminho")


async def pesquisa_info(anime: dict, limitador: asyncio.Semaphore) -> dict | None:
    async with limitador:
        tradutor = GT("en", "pt")
        try:
            anime["info"] = await anime_info_pesquisa(anime["id"])
        except Exception:
            return None
        link = anime["info"]["main_picture"]["large"]
        async with Client(timeout=40) as client:
            pagina = await client.get(link)
            imagem = pagina.content
        anime["imagem"] = imagem
        lista_negra = [":", "°", "?", "-", ",", "“", "”", ".", "\\", "/"]
        limpo = " ".join(
            [
                "".join([letra for letra in palavra if letra not in lista_negra])
                for palavra in anime["nome"].split()
            ]
        )
        anime["nome_pesquisa"] = anime["nome"]
        anime["nome"] = limpo
        logging.info(f"Nome do anime {limpo} tratado")
        anime["info"]["synopsis"] = tradutor.translate(
            ".".join(anime["info"]["synopsis"].split(".")[:-1])
        )
        anime["info"]["status"] = tradutor.translate(
            " ".join(anime["info"]["status"].split("_"))
        )
        anime["info"]["genres"] = [
            tradutor.translate(g["name"]) for g in anime["info"]["genres"]
        ]
        try:
            anime["info"]["broadcast"] = data_info(anime["info"]["broadcast"])
        except Exception:
            anime["info"]["broadcast"] = {}
        else:
            anime["info"]["broadcast"]["dia"] = tradutor.translate(
                anime["info"]["broadcast"]["dia"]
            )
        return anime


def series(anime: dict) -> pd.Series:
    anime = pd.Series(anime, name=anime["nome"])
    anime = anime.drop("nome")
    return anime


async def pesquisar(nome: str, func_log: Callable[[str], None]):
    animes = []
    func_log("Pesquisando animes no Erai...")
    while True:
        try:
            erai = await erai_animes.pesquisar(nome)
        except ErroCookie:
            await obter_cookies()
            continue
        except Exception:
            func_log("Erro ao pesquisar animes no Erai")
            erai = None
            break
        else:
            break
    if erai:
        func_log(f"{len(erai)} animes encontrados no Erai")
        animes.extend(erai)
    else:
        func_log("Nenhum anime encontrado no Erai")
    func_log("Pesquisando animes no TopAnimes...")
    top = await top_animes.pesquisar(nome)
    if top:
        func_log(f"{len(top)} animes encontrados no TopAnimes")
        animes.extend(top)
    else:
        func_log("Nenhum anime encontrado no TopAnimes")
    func_log("Pesquisando animes no Infinite...")
    infi = await infinite.pesquisar(nome)
    if infi:
        func_log(f"{len(infi)} encontrados no Infinite")
        animes.extend(infi)
    else:
        func_log("Nenhum anime encontrado no Infinite")
    limitador = asyncio.Semaphore(5)
    animes = [pesquisa_info(a, limitador) for a in animes]
    func_log(f"Pesquisando informações sobre {len(animes)} animes...")
    animes = await asyncio.gather(*animes)
    animes = [a for a in animes if a]
    animes = [series(anime) for anime in animes]
    animes = pd.DataFrame(animes)
    return animes


async def anime_info_pesquisa(id: int | None = None, nome: str | None = None):
    api = "https://api.myanimelist.net/v2"
    client_id = "a81a1ee7e886f2f0c54ec850594667a3"
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        "X-MAL-CLIENT-ID": client_id,
    }
    infos = [
        "title",
        "start_date",
        "end_date",
        "mean",
        "status",
        "genres",
        "num_episodes",
        "start_season",
        "broadcast",
        "source",
        "related_anime",
        "related_manga",
        "synopsis",
    ]

    async def info_id(id: int | None):
        async with Client(headers=header) as client:
            anime_info = await client.get(
                api + f"/anime/{id}", params={"fields": ",".join(infos)}
            )
            if anime_info.status_code != 200:
                raise Exception("Erro ao obter informações, descartando anime")
        return anime_info.json()

    async def pesquisa_id(nome: str | None):
        async with Client(headers=header) as client:
            anime = await client.get(api + "/anime", params={"q": nome})
        return anime.json()

    if id:
        anime = await info_id(id)
    else:
        anime = await pesquisa_id(nome)
        anime = anime["data"][0]["node"]["id"]
        anime = await info_id(anime)
    return anime


def data_info(broadcast):
    dia = broadcast["day_of_the_week"]
    hora = broadcast["start_time"]
    dias_da_semana = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thurday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }
    dia_esperado = dias_da_semana[dia.capitalize()]
    time = datetime.strptime(hora, "%H:%M").time()
    now_jst = datetime.now(ZoneInfo("Asia/Tokyo"))
    hj_jst = now_jst.date()
    dia_s_jst = hj_jst.weekday()
    days_ahead = (dia_esperado - dia_s_jst) % 7
    if days_ahead == 0 and now_jst.time() > time:
        days_ahead = 7
    dia_alvo = hj_jst + timedelta(days_ahead)
    dt_jst = datetime.combine(dia_alvo, time).replace(tzinfo=ZoneInfo("Asia/Tokyo"))
    data = dt_jst.astimezone(ZoneInfo("America/Sao_Paulo"))
    return {"dia": data.strftime("%A"), "hora": data.strftime("%H:%M")}


async def selecionar_ep(anime: pd.Series) -> pd.Series:
    if anime["server"] == "Erai":
        eps = await erai_animes.extrair_ep(anime["link"])
    elif anime["server"] == "TopAnimes":
        eps = await top_animes.episodios(anime["link"])
    elif anime["server"] == "Infinite":
        eps = await infinite.episodios(anime["link"])
    anime["ep"] = [{"ep": f"Episodio {ep}", "link": eps[ep]} for ep in eps.keys()]
    return anime


async def baixar_ep_erai(ep: dict):
    qbit = torrent.Qbit()
    await qbit.init_sessao()
    if qbit.sessao:
        await qbit.baixar(ep)


async def baixar_ep_top_animes(ep, frame: CTkFrame):
    frame_barra = CTkFrame(frame, fg_color="transparent")
    frame_barra.pack(fill="both", expand=True)
    label = CTkLabel(frame_barra, text=f"Baixando {ep['ep']}... 0%", font=("Arial", 15))
    label.pack(side="left", padx=10)
    barra = ctk.CTkProgressBar(frame_barra)
    barra.pack(expand=True, fill="x", padx=10)
    barra.set(0)

    def callback(progresso: float, velocidade: float):
        barra.set(progresso)
        label.configure(
            text=f"Baixando {ep['ep']}... {progresso * 100:.2f}%   {velocidade}"
        )

    await top_animes.baixar(ep, callback)


async def baixar_ep_infinite(ep, frame: CTkFrame):
    frame_barra = CTkFrame(frame, fg_color="transparent")
    frame_barra.pack(fill="both", expand=True)
    label = CTkLabel(frame_barra, text=f"Baixando {ep['ep']}... 0%", font=("Arial", 15))
    label.pack(side="left", padx=10)
    barra = ctk.CTkProgressBar(frame_barra)
    barra.pack(expand=True, fill="x", padx=10)
    barra.set(0)

    def callback(progresso: float, velocidade: float):
        barra.set(progresso)
        label.configure(
            text=f"Baixando {ep['ep']}... {progresso * 100:.2f}%   {velocidade}"
        )

    await infinite.baixar(ep, callback)


async def update(versao):
    link = "https://api.github.com/repos/SonyBlainy/Anime_Downloader/releases/latest"
    async with Client() as client:
        r = await client.get(link)
        data = r.json()
        if data["tag_name"] != versao:
            link = data["assets"][0]["browser_download_url"]
            caminho = os.path.expandvars(r"%temp%\anime_downloader_temp")
            os.makedirs(caminho, exist_ok=True)
            caminho = os.path.join(caminho, "instalador.exe")
            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "wget",
                    link,
                    "-UseBasicParsing",
                    "-O",
                    caminho,
                ],
                encoding="utf-8",
            )
            os.startfile(caminho)
    sys.exit()


def abrir_pasta(caminho: str):
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", "explorer", caminho],
        encoding="utf-8",
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def deletar_anime(anime: pd.Series, dados: pd.DataFrame) -> None:
    shutil.rmtree(anime["caminho"])
    dados = dados.drop(anime.name)
    with open("dados.parquet", "wb") as arquivo:
        dados.to_parquet(arquivo)


async def obter_cookies():
    cookies = await navegador.cookies()
    lista_cookies = [
        {i["name"]: i["value"]} for i in cookies if "wordpress_logged_in" in i["name"]
    ][0]
    with open("cookies.json", "w") as arquivo:
        json.dump(lista_cookies, arquivo, indent=4)


def verificar_navegador():
    if not os.path.exists(r".\chrome-win64"):
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        link = (
            "https://cdn.playwright.dev/builds/cft/147.0.7727.15/win64/chrome-win64.zip"
        )
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "curl.exe",
                "-L",
                "--progress-bar",
                "-A",
                f'"{user_agent}"',
                "-o",
                "chrome.zip",
                f'"{link}"',
            ]
        )
        with zipfile.ZipFile("chrome.zip") as arquivo:
            arquivo.extractall(".")
        os.remove("chrome.zip")


async def verifica_cookies():
    if not os.path.exists("cookies.json"):
        await obter_cookies()
    else:
        with open("cookies.json") as arquivo:
            cookie = json.load(arquivo)
        for a in cookie.keys():
            if "wordpress_logged_in" in a:
                return
        await obter_cookies()


def adicionar_anime(data: pd.DataFrame, anime: pd.Series) -> None:
    if anime["id"] not in data["id"].values:
        data.loc[anime.name] = anime
        with open("dados.parquet", "wb") as arquivo:
            data.to_parquet(arquivo)


def criar_pasta(anime: pd.Series, existe=False) -> pd.Series:
    caminho = "_".join(anime.name.__str__().split())
    caminho = os.path.join(path, caminho) + f"-{anime['id']}"
    os.makedirs(caminho, exist_ok=True)
    anime["caminho"] = caminho
    return anime


def verificar_animes(animes_data: pd.DataFrame) -> pd.DataFrame:
    ids = [int(re.search(r"-(\d*)$", id).group(1)) for id in os.listdir(path)]
    for id in animes_data["id"]:
        if id not in ids:
            animes_data = animes_data[animes_data["id"] != id]
    for d in os.scandir(path):
        id = int(re.search(r"-(\d*)$", d.name).group(1))
        if id not in animes_data["id"].values:
            shutil.rmtree(d.path)
    with open("dados.parquet", "wb") as arquivo:
        animes_data.to_parquet(arquivo)
    return animes_data


def mover_arquivo(arquivo: str, destino: str):
    shutil.move(arquivo, destino)
