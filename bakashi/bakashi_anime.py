import requests
from lxml.html import fromstring
from urllib.parse import unquote
import re
import yt_dlp
import json

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
        ep = player({'nome': nome, 'link': link})
        if ep:
            lista.append(ep)
    if not lista:
        return None
    anime.ep = lista
    return anime

def player(ep):
    r = fromstring(requests.get(ep['link']).content)
    pagina = r.find('.//div[@id="dooplay_player_content"]').findall('.div')[1:]
    pagina = [i.find('div/iframe').get('data-litespeed-src') for i in pagina]
    pagina2 = [i for i in pagina if 'blogger.com' in i]
    pagina2.extend([i for i in pagina if 'q1n.net/antivirus2' in i])
    pagina = [unquote(re.findall(r'\?url=(.*$)', i)[0]) for i in pagina if '?url=' in i]
    pagina.extend(pagina2)
    fontes = {'csst.online': lambda link: ruplay(link), 'blogger.com': lambda link: blogger(link),
              }
    for fonte in fontes.keys():
        for p in pagina:
            if fonte in p:
                try:
                    ep['link'], ep['estensao'] = fontes[fonte](p)
                    return ep
                except:
                    continue
    return None

def ruplay(link):
    r = fromstring(requests.get(link).content)
    link = r.find('body/script').xpath('text()')[0]
    pattern = r'var player = new Playerjs\({[^}]*file:"([^"]+)"'
    t = re.findall(pattern, link)[-1]
    link = re.search(r'\[1080p\](.*$)', t).group(1)
    estensao = re.search(r'/[\d]*(\.[\w]*)/', link).group(1)
    return link, estensao

def blogger(link):
    yt_config = {
        'quiet': True,
        'no_warnings': True,
        'get_url': True
    }
    with yt_dlp.YoutubeDL(yt_config) as ydl:
        link = ydl.extract_info(link, download=False)['url']
    return link, '.mp4'

def qn1(link):
    r = fromstring(requests.get(link).content)
    link = r.find('body/script').xpath('text()')[0]
    link = re.findall(r'sources: \[(.*)\],', link)[0]
    link = json.loads(link)
    link = link.get('file')
    head = {'Referer': 'https://q1n.net/', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    links = str(requests.get(link, headers=head).content, 'utf-8')
    links = re.findall(r'(https://.*)\r\n', links)
    return links, '.mp4'