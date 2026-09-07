from httpx import AsyncClient as Client
from httpx import ConnectTimeout
import json
import re
from bs4 import BeautifulSoup
import os
import logging
import asyncio


if not os.path.exists("cookies.json"):
    with open("cookies.json", "w") as arquivo:
        json.dump({"sim": "sim"}, arquivo)

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}


class ErroCookie(Exception):
    def __init__(self):
        super().__init__("Erro ao utilizar cookie")


def ler_cookies():
    with open("cookies.json") as arquivo:
        return json.load(arquivo)


async def pagina_anime(link: str, limitador: asyncio.Semaphore):
    async with limitador:
        cookie = ler_cookies()
        async with Client(headers=header, cookies=cookie) as client:
            try:
                anime = await client.get(link)
            except ConnectTimeout:
                return None
            anime = BeautifulSoup(anime.content, "html.parser")
            nome = anime.select_one("#main h1").text
            id = anime.find("a", text=re.compile("MAL"))
            id = id.get("href")
            id = re.search(r"/anime/(\d*)", id).group(1)
        return {"nome": nome, "link": link, "id": int(id), "server": "Erai"}


async def pesquisar(nome: str):
    cookie = ler_cookies()
    async with Client(headers=header, cookies=cookie, timeout=50) as client:
        if len(nome.split()) > 1:
            nome = "+".join(nome.split())
        api = "https://www.erai-raws.info/?s=" + nome
        try:
            reque = await client.get(api)
            if reque.status_code != 200:
                logging.error(f"Erro {reque.status_code} ao acessar a pagina do Erai")
            else:
                r = BeautifulSoup(reque.content, "html.parser")
        except Exception:
            logging.error("Erro ao requisitar a pagina HTML", exc_info=True)
    animes = r.select_one(".search-results-list")
    if not animes:
        if not r.select(".not-found"):
            raise ErroCookie()
        else:
            return None
    animes = animes.select("table tr")
    animes = [anime.find("a").get("href") for anime in animes]
    limitador = asyncio.Semaphore(5)
    resultado = [pagina_anime(anime, limitador) for anime in animes]
    resultado = await asyncio.gather(*resultado, return_exceptions=True)
    resultado = [a for a in resultado if not isinstance(a, Exception)]
    return resultado


async def extrair_ep(link: str):
    cookie = ler_cookies()
    async with Client(headers=header, cookies=cookie) as client:
        pagina = await client.get(link)
        pagina = BeautifulSoup(pagina.content, "html.parser")
    eps = pagina.select_one(".tab-content")
    no_ar_lista = pagina.select("#menu1>table")
    no_ar_lista = [
        i
        for i in no_ar_lista
        if i.select_one('tr:nth-child(2)>th>span[data-title="Portuguese(Brazil)"]')
    ]
    heavc_lista = eps.select("#menu5>table")
    batch = eps.select("#menu3>table")
    filmes = eps.select("#menu4>table")
    pagina_load = pagina.find("script", id="erai-main-js-extra")
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
    if pagina_load:
        pagina_load = pagina_load.text
        pagina_load = re.search(r"var load_more_0_params=(\{[\s\S]*?\});", pagina_load)
        if pagina_load:
            pagina_load = json.loads(pagina_load.group(1))
            header_ajax = header.copy()
            header_ajax["Referer"] = link
            async with Client(headers=header_ajax, cookies=cookie) as navegador:
                pagina_ajax = await navegador.post(
                    pagina_load["ajaxurl"],
                    data={
                        "action": "load_more_0",
                        "page": "2",
                        "post_id": pagina_load["post_id"],
                        "security": pagina_load["security"],
                    },
                )
                pagina_ajax = BeautifulSoup(pagina_ajax.content, "html.parser")
            pagina_ajax = pagina_ajax.select("table")
            no_ar_lista.extend(pagina_ajax)
    for ep in reversed(no_ar_lista):
        ep_elemento_texto = ep.select_one("tr>th>a:nth-child(2)").text
        paren = re.findall(r"\((.*?)\)", ep_elemento_texto)
        if "Korean Audio" not in paren and "Chinese Audio" not in paren:
            tipo = ep.select_one("tr>th>a").get("data-title")
            if tipo == "Encodings":
                nome = re.search(r" - ([\w\.]*) ", ep_elemento_texto).group(1)
                link = ep.select("tr")[-1]
                link = link.find("a", text="magnet").get("href")
                heavc[nome] = link
            elif tipo in ["Airing", "Batch", "Movie of Special Episode"]:
                if tipo == "Movie of Special Episode":
                    nome = re.search(r" - (.*)$", ep_elemento_texto).group(1)
                    nome = nome.strip()
                else:
                    nome = re.search(r" - ([\w\.]*) ", ep_elemento_texto).group(1)
                link = ep.find("span", text=re.compile(r"1080p "))
                link = link.parent
                link = link.find("a", text="magnet").get("href")
                noar[nome] = link
    filtro = heavc.copy()
    filtro.update({k: v for k, v in noar.items() if k not in heavc.keys()})
    return filtro
