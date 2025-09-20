import os
from lxml.html import fromstring
import requests
import re

def pesquisar(nome:str):
    if len(nome.split()) > 1:
        nome = '-'.join(nome.split())
    api = f'https://infinitefansub.com/pesquisa/{nome}'
    pagina = fromstring(requests.get(api).content)
    animes = pagina.find_class('anime-list')[0].find_class('anime')
    resultado = []
    for anime in animes:
        link = anime.get('onclick')
        nome = anime.find('span').text
        link = re.findall(r"'(.*)'", link)[0]
        link = '/'.join(api.split('/')[:3])+link
        dados = {'nome': nome, 'link': link}
        resultado.append(dados)
    return resultado

def episodios(anime):
    pagina = fromstring(requests.get(anime.link).content)
    eps = pagina.find_class('episode-list')[0].findall('div')
    eps = [{'nome': ep.find('header/span').text, 'link': ep.find('aside/div/div[2]/span[2]/a').get('href')} for ep in eps]
    anime.ep = eps
    return anime