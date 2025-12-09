import requests
import json
import re
from erai import torrent
from lxml.html import fromstring
import os
import logging

save = os.getenv('save')
path = os.getenv('caminho')
cookie = json.load(open('cookies.json'))
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'}

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
    resultado = []
    for anime in animes:
        link = anime.find('div/header/h2/a')
        nome = link.xpath('text()')[0]
        link = link.get('href')
        pagina = fromstring(requests.get(link, headers=header, cookies=cookie).content)
        imagem = pagina.find_class('entry-content-poster')[0].find('img').get('src')
        imagem = requests.get(imagem).content
        resultado.append({'nome': nome, 'link': link, 'imagem': imagem})
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
                
def baixar_anime(anime):
    if not anime.ep:
        return None
    else:
        qbit = torrent.Qbit()
        if not qbit.sessao:
            logging.error('Erro ao iniciar o Qbit')
            return None
        if isinstance(anime.ep, list):
            logging.info(f'Baixando {len(anime.ep)} episodios')
            for ep in anime.ep:
                qbit.baixar(ep)
                logging.info(f'Episodio {ep.nome.split()[1]} baixado')
        else:
            qbit.baixar(anime.ep)
            logging.info(f'Episodio {anime.ep.nome.split()[1]} baixado')
