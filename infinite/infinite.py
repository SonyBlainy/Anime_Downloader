from httpx import AsyncClient as Client
from bs4 import BeautifulSoup
import re

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}


async def pesquisar(nome: str):
    if len(nome.split()) > 1:
        nome = "-".join(nome.split())
    api = f"https://infinitefansub.com/pesquisa/{nome}"
    async with Client(headers=header) as navegador:
        pagina = await navegador.get(api)
        pagina = pagina.content
    pagina = BeautifulSoup(pagina, "html.parser")
    animes = pagina.select(".anime-list>.anime")
    resultado = []
    for anime in animes:
        link = anime["onclick"]
        nome = anime.select_one(":scope>span").text
        link = re.search(r"'(.*)'", link).group(1)
        link = "/".join(api.split("/")[:-2]) + link
        dados = {"nome": nome, "link": link, "server": "Infinite"}
        resultado.append(dados)
    return resultado


async def episodios(link: str):
    async with Client(headers=header) as navegador:
        pagina = await navegador.get(link)
        pagina = pagina.content
    pagina = BeautifulSoup(pagina, "html.parser")
    eps = pagina.select(".episode-list>.episode-container")
    resultado = {}
    for ep in eps:
        nome = ep.select_one("span").text.split("-")[0]
        nome = nome.split()[-1]
        link = ep.select_one(".episode-links>span:nth-of-type(2)>a")["href"]
        resultado[nome] = link
    return resultado
