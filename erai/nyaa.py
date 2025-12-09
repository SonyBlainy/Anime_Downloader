import requests
import json
import re
from lxml import etree
from lxml.html import fromstring
import os
import logging
from multiprocessing import Pool

save = os.getenv('save')
path = os.getenv('caminho')
cookie = json.load(open('cookies.json'))
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'}

def pagina_anime(anime):
    anime = fromstring(anime)
    link = anime.find('div/header/h2/a')
    nome = link.xpath('text()')[0]
    link = link.get('href')
    pagina = fromstring(requests.get(link, headers=header, cookies=cookie).content)
    imagem = pagina.find_class('entry-content-poster')[0].find('img').get('src')
    try:
        imagem = requests.get(imagem).content
    except:
        imagem = open(r'icones\erro.png', 'rb')
    return {'nome': nome, 'link': link, 'imagem': imagem}

def pesquisar(nome:str):
    if len(nome.split()) > 1:
        nome = '+'.join(nome.split())
    api = 'https://www.erai-raws.info/?s='+nome
    try:
        reque = requests.get(api, headers=header, cookies=cookie)
        if reque.status_code != 200:
            logging.error(f'Erro {reque.status_code} ao acessar a pagina do Erai')
        else:
            r = fromstring(reque.content)
    except requests.RequestException as e:
        logging.error(f'Erro ao requisitar a pagina HTML: {e}')
    animes = r.get_element_by_id('main').findall('article')
    if not animes:
        return None
    resultado = []
    animes = [etree.tostring(a, encoding='unicode') for a in animes]
    with Pool(20) as pool:
        resultado = pool.map(pagina_anime, animes)
    return resultado

def extrair_ep(link: str):
    pagina = fromstring(requests.get(link, headers=header, cookies=cookie).content)
    eps = pagina.get_element_by_id('menu0').findall('table')
    noar = {}
    heavc = {}
    for ep in eps.__reversed__():
        if ep.find('tr/th/a').get('data-title') != 'Subtitle':
            nome = ep.find('tr/th/a[2]').xpath('text()')[0].strip().split('-')[-1]
            colchetes = re.findall(r'\((.*?)\)', nome)
            if colchetes:
                if 'HEVC' in colchetes and 'Chinese Audio' not in colchetes:
                    nome = ' '.join(nome.split()[:-1]).strip()
                    link = ep.find('tr[4]/th/a[2]').get('href')
                    heavc[nome] = link
                    continue
            else:
                link = ep.find('tr[4]/th/a[2]').get('href')
                noar[nome.strip()] = link
    filtro = heavc.copy()
    filtro.update({k: v for k, v in noar.items() if k not in heavc.keys()})
    return filtro
                