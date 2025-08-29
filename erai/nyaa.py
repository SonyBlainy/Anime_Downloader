import requests
import re
from fera.animes_geral import obter_escolha_valida as ob
from erai import torrent
from lxml.html import fromstring
import os
import logging

save = os.getenv('save')
path = os.getenv('caminho')
cookie = {'wordpress_logged_in_25c65adc7d24c2f6075a3cbdddcf4db0': 'sonyblainy%7C1782488870%7CtagV6OIs9GVUlh1bzkgWrcAwYfpElhFfxmC04xAO1PB%7C13cd2e304dcb43faa3f501f5ca7fb5300213fb4a2705b5be4c0dfcfc9112e399',
    '__ddg5_': 'fjpDyDZhBkfRRaUj'}

def pesquisar(nome:str):
    if len(nome.split()) > 1:
        nome = '+'.join(nome.split())
    api = 'https://www.erai-raws.info/?s='+nome
    try:
        reque = requests.get(api, cookies=cookie)
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
        resultado.append({'nome': nome, 'link': link})
    print('='*30)
    for i, a in enumerate(resultado):
        print(f'[{i}] {a["nome"]}')
    esco = ob('Escolha um anime ou digite sair: ', (0, len(resultado)), True)
    if not isinstance(esco, int):
        return None
    resultado = resultado[esco]
    resultado = extrair_ep(resultado)
    return resultado

def extrair_ep(anime: dict):
    pagina = fromstring(requests.get(anime['link'], cookies=cookie).content)
    eps = pagina.get_element_by_id('menu0').findall('table')
    noar = {}
    heavc = {}
    for ep in eps:
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
    anime['eps'] = filtro
    return anime
                

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
