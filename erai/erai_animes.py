from httpx import AsyncClient as Client
from httpx import ReadTimeout
import json
import re
from bs4 import BeautifulSoup
import os
import logging
import asyncio

path = os.getenv("caminho")

if not os.path.exists("cookies.json"):
    with open("cookies.json", "w") as arquivo:
        json.dump({"sim": "sim"}, arquivo)

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}


class ErroCookie(Exception):
    def __init__(self):
        super().__init__("Erro ao utilizar cookie")


def divisao_lista(lista, tamanho=5):
    for i in range(0, len(lista), tamanho):
        yield lista[i : i + tamanho]


def ler_cookies():
    with open("cookies.json") as arquivo:
        return json.load(arquivo)


async def pagina_anime(link):
    cookie = ler_cookies()
    async with Client(headers=header, cookies=cookie) as client:
        try:
            anime = await client.get(link)
        except ReadTimeout:
            return None
        anime = BeautifulSoup(anime.content, "html.parser")
        nome = anime.select_one("#main h1").text
        id = anime.find("a", text=re.compile("MAL"))
        id = id.get("href")
        id = re.search(r"/anime/(\d*)", id).group(1)
    return {"nome": nome, "link": link, "id": int(id), "server": "Erai"}


async def pesquisar(nome: str):
    cookie = ler_cookies()
    async with Client(headers=header, cookies=cookie) as client:
        if len(nome.split()) > 1:
            nome = "+".join(nome.split())
        api = "https://www.erai-raws.info/?s=" + nome
        try:
            reque = await client.get(api)
            if reque.status_code != 200:
                logging.error(f"Erro {reque.status_code} ao acessar a pagina do Erai")
            else:
                r = BeautifulSoup(reque.content, "html.parser")
        except:
            logging.error(f"Erro ao requisitar a pagina HTML", exc_info=True)
    animes = r.select_one(".search-results-list")
    if not animes:
        if not r.select(".not-found"):
            raise ErroCookie()
        else:
            return None
    animes = animes.select("table tr")
    animes = [anime.find("a").get("href") for anime in animes]
    lista = []
    resultado = [pagina_anime(anime) for anime in animes]
    for chunk in divisao_lista(resultado):
        c = await asyncio.gather(*chunk)
        lista.extend([a for a in c if a])
    return lista


async def extrair_ep(link: str):
    cookie = ler_cookies()
    async with Client(headers=header, cookies=cookie) as client:
        pagina = await client.get(link)
        pagina = BeautifulSoup(pagina.content, "html.parser")
        pagina = pagina.select_one(".tab-content")
    no_ar_lista = pagina.select("#menu1>table")
    no_ar_lista = [
        i
        for i in no_ar_lista
        if i.select_one('tr:nth-child(2)>th>span[data-title="Portuguese(Brazil)"]')
    ]
    heavc_lista = pagina.select("#menu5>table")
    batch = pagina.select("#menu3>table")
    filmes = pagina.select("#menu4>table")
    if heavc_lista:
        heavc_lista = [
            i
            for i in heavc_lista
            if i.select_one('tr:nth-child(2)>th>span[data-title="Portuguese(Brazil)"]')
        ]
        no_ar_lista.extend(heavc_lista)
    if batch:
        no_ar_lista.extend(
            [
                i
                for i in batch
                if i.select_one(
                    'tr:nth-child(2)>th>span[data-title="Portuguese(Brazil)"]'
                )
            ]
        )
    if filmes:
        no_ar_lista.extend(
            [
                i
                for i in filmes
                if i.select_one(
                    'tr:nth-child(2)>th>span[data-title="Portuguese(Brazil)"]'
                )
            ]
        )
    heavc = {}
    noar = {}
    for ep in reversed(no_ar_lista):
        if ep.select_one('a[data-title="Encodings"]'):
            nome = ep.select_one("tr>th>a:nth-child(2)").text
            nome = re.search(r" - (\w*) ", nome).group(1)
            link = ep.select("tr")[-1]
            link = link.find("a", text="magnet").get("href")
            heavc[nome] = link
        elif (
            ep.select_one('a[data-title="Airing"]')
            or ep.select_one('a[data-title="Batch"]')
            or ep.select_one('a[data-title="Movie or Special Episode"]')
        ):
            nome = ep.select_one("tr>th>a:nth-child(2)").text
            if ep.select_one('a[data-title="Movie or Special Episode"]'):
                nome = re.search(r" - (.*)$", nome).group(1)
                nome = nome.strip()
            else:
                nome = re.search(r" - (\w*) ", nome).group(1)
            link = ep.find("span", text=re.compile(r"1080p "))
            link = link.parent
            link = link.find("a", text="magnet").get("href")
            noar[nome] = link
    filtro = heavc.copy()
    filtro.update({k: v for k, v in noar.items() if k not in heavc.keys()})
    return filtro
