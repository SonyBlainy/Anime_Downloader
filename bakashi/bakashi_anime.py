import requests
from lxml.html import fromstring
import re
from urllib.parse import unquote

def pesquisar(nome: str) -> list:
    api = 'https://q1n.net/'
    if len(nome.split()) > 1:
        nome = '+'.join(nome.split())
    r = fromstring(requests.get(api, params={'s': nome}).content)
    animes = r.find_class('result-item')
    lista = []
    for a in animes:
        dados = a.find('article')
        dados = dados.xpath('div')[1]
        dados = dados.find('div[1]/a')
        link = dados.get('href')
        nome = dados.text
        dados = {'nome': nome, 'link': link}
        lista.append(dados)
    return lista

def episodios(anime):
    lista = []
    r = fromstring(requests.get(anime.link).content)
    eps = r.find_class('episodios')[0].findall('li')
    for ep in eps:
        link = ep.find_class('episodiotitle')[0].find('a')
        nome = link.text
        link = link.get('href')
        lista.append({'nome': nome, 'link': link})
    if not lista:
        return None
    anime.ep = lista
    return anime

def player(ep):
    r = fromstring(requests.get(ep.link).content)
    video = ''
    pagina = r.find('.//div[@id="dooplay_player_content"]').findall('.div')[1:]
    for i in pagina:
        if 'csst.online' in i.find('div/iframe').get('data-litespeed-src'):
            video = i.find('div/iframe').get('data-litespeed-src')
            break
    if 'aviso' in video:
        video = unquote(video).split('=')[-1]
    if not video:
        return None, ep
    r = fromstring(requests.get(video).content)
    link = r.find('.body/script').xpath('text()')[0]
    pattern = r'var player = new Playerjs\({[^}]*file:"([^"]+)"'
    t = re.findall(pattern, link)[-1]
    link = re.search(r'\[1080p\](.*$)', t).group(1)
    estensao = re.search(r'/[\d]*(\.[\w]*)/', link).group(1)
    ep.estensao = estensao
    ep.nome += estensao
    ep.link = link
    return ep
