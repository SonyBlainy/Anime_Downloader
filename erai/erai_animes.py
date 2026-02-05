from httpx import AsyncClient as Client
import json
import re
from lxml.html import fromstring
import os
import logging
import asyncio

save = os.getenv('save')
path = os.getenv('caminho')
cookie = json.load(open('cookies.json'))
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'}

client = Client(headers=header,
                cookies=cookie,
                timeout=30)


def divisao_lista(lista, tamanho=10):
    for i in range(0, len(lista), tamanho):
        yield lista[i:i+tamanho]

async def pagina_anime(link):
    anime = await client.get(link)
    anime = fromstring(anime.content)
    nome = anime.get_element_by_id('main').find('.//h1').xpath('text()')[0]
    imagem = anime.find_class('entry-content-poster')[0].find('img').get('src')
    try:
        imagem = await client.get(imagem)
        imagem = imagem.content
    except:
        imagem = open(r'icones\erro.png', 'rb')
    return {'nome': nome, 'link': link, 'imagem': imagem}

async def pesquisar(nome:str):
    if len(nome.split()) > 1:
        nome = '+'.join(nome.split())
    api = 'https://www.erai-raws.info/?s='+nome
    try:
        reque = await client.get(api)
        if reque.status_code != 200:
            logging.error(f'Erro {reque.status_code} ao acessar a pagina do Erai')
        else:
            r = fromstring(reque.content)
    except:
        logging.error(f'Erro ao requisitar a pagina HTML', exc_info=True)
    animes = r.get_element_by_id('main').findall('article')
    if not animes:
        return None
    animes = [anime.find('.//a').get('href') for anime in animes]
    lista = []
    resultado = [pagina_anime(anime) for anime in animes]
    for chunk in divisao_lista(resultado):
        c = await asyncio.gather(*chunk)
        lista.extend(c)
    return lista

async def extrair_ep(link: str):
    pagina = await client.get(link)
    pagina = fromstring(pagina.content)
    eps = pagina.get_element_by_id('menu0').findall('table')
    noar = {}
    heavc = {}
    for ep in reversed(eps):
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
                