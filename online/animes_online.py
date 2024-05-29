from sakura.Sakura import Anime, Ep
import requests
from lxml.html import fromstring

def pesquisar(nome: str) -> list:
    api = 'https://animesonline.nz/?s='
    if len(nome.split()) > 1:
        nome = '+'.join(nome.split())
    r = fromstring(requests.get(api+nome).content)
    animes = r.find_class('result-item')
    lista = []
    for a in animes:
        dados = a.find('article')
        dados = dados.xpath('div')[1]
        dados = dados.find('div[1]/a')
        link = dados.get('href')
        nome = dados.text
        anime = Anime(nome, link)
        lista.append(anime)
    return lista

def episodios(anime: Anime) -> Anime:
    r = fromstring(requests.get(anime.link).content)
    eps = r.find_class('episodios')[0].xpath('li')
    lista = []
    for ep in eps:
        nome = ep.find_class('episodiotitle')[0].find('a')
        link = nome.get('href')
        nome = nome.text
        r = fromstring(requests.get(link).content)
        links = [l.get('src') for l in r.find_class('metaframe rptss')]
        for l in links:
            if 'csst.online' in l:
                res = fromstring(requests.get(l).content)
                var = res.xpath('body/script')[0].text
                var = var.split('var')[2].split('(')[1].split(')')[0]
                var = var.split('[1080p]')[1].split('"')[0][:-1]
                break
        ep = Ep(nome, var, '.'+var.split('.')[-1], 'online')
        lista.append(ep)
    anime.ep = lista
    return anime

