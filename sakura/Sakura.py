import random
import base64
import json
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
        animes.append({'nome': nome, 'link': link})
    return animes
    
def listar_episodios(anime):
    resposta = fromstring(requests.get(anime.link).content)
    for a in ['fhd', 'hd']:
        links = resposta.find(f'.//div[@id="{a}"]')
        media_fire = links.findall('table[1]/tr/td/a')
        if not media_fire:
            continue
        else:
            try:
                link = [a for a in media_fire if a.text_content().strip() == 'Mediafire'][0]
            except:
                eps = links.findall('table[2]/tr')
                eps = [{'nome': e.find('td').text, 'link': e.find('td[2]/a').get('href')} for e in eps if e.find('td[2]/a/span').text == 'Mediafire']
                anime.ep = eps
            else:
                link = fromstring(requests.get(link.get('href')).content).find_class('w-full')[0].find('a').get('href')
                while True:
                    try:
                        link = ouo_bypass(link)['bypassed_link']
                    except:
                        continue
                    else:
                        break
                eps = mediafire_pasta(link)
                eps = [{'nome': e['filename'], 'link': e['links']['normal_download']} for e in eps]
                anime.ep = eps
    return anime
    
def mediafire_pasta(link: str):
    api = 'https://www.mediafire.com/api/1.4/folder/get_content.php'
    key = link.split('/')[-2]
    parame = {'content_type': 'files', 'filter': 'all', 'order_by': 'name', 'order_direction': 'asc',
              'chunk': 1, 'version': 1.5, 'folder_key': key, 'response_format': 'json'}
    eps = json.loads(requests.get(api, params=parame).content)['response']['folder_content']['files']
    return eps
    
def link_ep_mediafire(ep):
    if isinstance(ep, list):
        for e in ep:
            pagina = fromstring(requests.get(e.link).content)
            link = pagina.find_class('download_link')[0].find('a[@id="downloadButton"]').get('data-scrambled-url')
            if not link:
                link = pagina.find_class('download_link')[0].find('a[@id="downloadButton"]').get('href')
            else:
                link = base64.decodebytes(link.encode()).decode()
            e.nome = pagina.find_class('dl-btn-label')[0].get('title')
            e.link = link
    else:
        pagina = fromstring(requests.get(ep.link).content)
        link = pagina.find_class('download_link')[0].find('a[@id="downloadButton"]').get('data-scrambled-url')
        if not link:
            link = pagina.find_class('download_link')[0].find('a[@id="downloadButton"]').get('href')
        else:  
            link = base64.decodebytes(link.encode()).decode()
        ep.nome = pagina.find_class('dl-btn-label')[0].get('title')
        ep.link = link
    return ep

def sakura_link(ep):
    link = fromstring(requests.get(ep.link).content).find_class('w-full')[0].find('a').get('href')
    while True:
        try:
            link = ouo_bypass(link)['bypassed_link']
        except:
            continue
        else:
            break
    ep.link = link
    return ep
