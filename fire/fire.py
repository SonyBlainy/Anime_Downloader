import os
import requests
from sakura.Sakura import Anime, Ep
from sakura.baixarep import baixarar as baixando
from lxml.html import fromstring

def pesquisa(anime: str) -> list:
    api = 'https://animefire.plus/pesquisar/'
    if len(anime.split()) > 1:
        anime = '-'.join(anime.split())
    r = requests.get(api+anime)
    r = fromstring(r.content)
    animes = r.find_class('mr-1')[0]
    animes = animes.xpath('div')
    lista = []
    for a in animes:
        nome = ' '.join(a.get('title').split()[:-4])
        link = a.find('article').find('a').get('href')
        anime = Anime(nome, link)
        lista.append(anime)
    return lista

def episodios(anime: Anime) -> Anime:
    r = requests.get(anime.link)
    r = fromstring(r.content)
    eps = r.find_class('div_video_list')[0]
    eps = eps.xpath('a')
    lista = []
    for ep in eps:
        link = ep.get('href')
        nome = ep.text.split('-')[1].strip()
        r = fromstring(requests.get(link).content)
        link = r.get_element_by_id('dw').get('href')
        r = fromstring(requests.get(link).content)
        link = r.find_class('d-block')[0]
        link = link.find_class('d-flex')[0]
        link = link.xpath('a')[-1].get('href').split('?')[0]
        est = '.'+link.split('.')[-1]
        lista.append(Ep(nome, link, est, 'Fire'))
    anime.ep = lista
    return anime

def baixar(anime: Anime) -> None:
    baixando(anime.ep.link, anime.ep.nome, anime.ep.caminho)
