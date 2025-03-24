import random
import json
import cloudscraper
import requests.cookies
from drivee.core import Anime, Ep
import requests
from lxml.html import fromstring
from ouo_bypass import ouo_bypass

def assinatura():
    numero = random.random() + 1
    base36 = format(int(numero*1e10), 'x')[2:7]
    return base36

def pesquisar_anime(anime):
    sessao = requests.Session()
    pagina = fromstring(sessao.get('https://www.sakuraanimes.com').content)
    csrf_token = pagina.find('head/meta[@name="csrf-token"]').get('content')
    wire_data = pagina.find_class('col-lg-9 bg-default')[0].find('div/div').get('wire:initial-data')
    wire_data = json.loads(wire_data)
    update = [{'type': 'syncInput', 'payload': {'id': assinatura(), 'name': 'search', 'value': anime}}]
    fingerprint = wire_data['fingerprint']
    servermemo = wire_data['serverMemo']
    payload = {'fingerprint': fingerprint, 'serverMemo': servermemo, 'updates': update}
    api = 'https://www.sakuraanimes.com/livewire/message/global-search'
    header = {'Content-Type': 'application/json', 'Accept': 'text/html, application/xhtml+xml',
              'X-Livewire': 'true', 'X-Csrf-Token': csrf_token, 'Accept-Encoding': 'gzip, deflate',
              'Priority': 'u=1, i', 'Origin': 'https://www.sakuraanimes.com', 'Referer': 'https://www.sakuraanimes.com/',
              'Sec-Fetch-Site': 'same-origin'}
    biscoito = sessao.cookies
    resposta = sessao.post(api, json=payload, headers=header, cookies=biscoito).content
    resposta = fromstring(json.loads(resposta)['effects']['html']).find('.//div[@id="search-box"]').findall('ul/li')
    animes = []
    for anime in resposta:
        anime = anime.find('a')
        link = anime.get('href')
        nome = ' '.join(anime.text.split()[:-1])
        animes.append(Anime(nome, link))
    return animes
    
def listar_episodios(anime: Anime):
    resposta = fromstring(requests.get(anime.link).content)
    links = resposta.find('.//div[@id="fhd"]')
    media_fire = links.findall('table/tr/td/a')
    for link in media_fire:
        if link.text_content().strip() == 'Mediafire':
            link = link.get('href')
            break
    link = fromstring(requests.get(link).content).find_class('w-full')[0].find('a').get('href')
    link = ouo_bypass(link)['bypassed_link']
    eps = mediafire_pasta(link)
    anime.ep = eps
    return anime
    
def mediafire_pasta(link: str):
    api = 'https://www.mediafire.com/api/1.4/folder/get_content.php'
    key = link.split('/')[-2]
    parame = {'content_type': 'files', 'filter': 'all', 'order_by': 'name', 'order_direction': 'asc',
              'chunk': 1, 'version': 1.5, 'folder_key': key, 'response_format': 'json'}
    eps = json.loads(requests.get(api, params=parame).content)['response']['folder_content']['files']
    eps = [Ep(ep['filename'], ep['links']['normal_download'], f'.{ep['filename'].split('.')[-1]}',
              'Mediafire') for ep in eps]
    return eps
    
def link_ep_mediafire(ep: Ep|list):
    cloudpass = cloudscraper.create_scraper()
    if isinstance(ep, list):
        for e in ep:
            while True:
                pagina = fromstring(cloudpass.get(e.link).text)
                link = pagina.find_class('download_link')[0].find('a[@id="downloadButton"]').get('href')
                if 'download' in link:
                    break
                else:
                    cloudpass = cloudscraper.create_scraper()
            e.link = link
    else:
        while True:
            pagina = fromstring(cloudpass.get(ep.link).text)
            link = pagina.find_class('download_link')[0].find('a[@id="downloadButton"]').get('href')
            if 'download' in link:
                break
            else:
                cloudpass = cloudscraper.create_scraper()
        ep.link = link
    return ep
