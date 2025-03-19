import requests
import re
from lxml.html import fromstring
import os
import logging
save = os.getenv('save')
path = os.getenv('caminho')

def pesquisar(nome:str):
    if len(nome.split()) > 1:
        nome = '+'.join(nome.split())
    api = 'https://nyaa.land/user/Erai-raws'
    post = {'f':0, 'c':'0_0', 'q':nome}
    try:
        reque = requests.get(api, params=post)
        if reque.status_code != 200:
            logging.error(f'Erro {reque.status_code} ao acessar a pagina do Nyaa')
        else:
            r = fromstring(reque.content)
    except requests.RequestException as e:
        logging.error(f'Erro ao requisitar a pagina HTML: {e}')
    page = r.find_class('center')[0].find_class('pagination')
    if len(page) > 0:
        contador = 1
        resultado = busca(r)
        logging.info(f'Pagina número 1 analisada, {len(resultado)} animes encontrados atualmente')
        while True:
            page = r.find_class('center')[0].find_class('pagination')[0]
            try:
                link = 'https://nyaa.land'+page.find_class('next')[0].find('a').get('href')
            except:
                break
            else:
                r = fromstring(requests.get(link).content)
                resultado = busca(r, resultado)
                contador += 1
                logging.info(f'Pagina número {contador} analisada, {len(resultado)} animes encontrados atualmente')
    else:
        resultado = busca(r)
        logging.info(f'Pagina analisada, {len(resultado)} animes encontrados')
    return resultado

def extrair_nome(nome):
    nome = nome.split('-')
    nome = [p.strip() for p in nome]
    for posi, i in enumerate(nome):
        if i[0].isnumeric() and '[' in i:
            anime_nome = nome[1:posi]
            break
    if len(anime_nome) > 1:
        copia = anime_nome.copy()
        for p in copia:
            if copia.index(p) == 0:
                anime_nome = ' '.join(p.split()[1:])
            else:
                anime_nome += f' {p}'
    else:
        anime_nome = ' '.join(anime_nome[0].split()[1:])
    ep = '-'.join(nome[posi:])
    if '~' not in ep:
        colchetes = re.findall(r'\[(.*?)\]', ep)
        if len(colchetes[0].split()) > 1:
            copia = colchetes[1:]
            colchetes = colchetes[0].split()
            for i in copia:
                colchetes.append(i)
        ep = ep.split()[0]
        logging.info(f'Informacoes do episodio {ep} do anime {anime_nome} extraidas')
        return [anime_nome, ep, colchetes]
    else:
        return None

def filtrar(info, lista, link):
    if lista.get(info[0]) == None:
        if 'HEVC' in info[2] or '1080p' in info[2]:
            if 'Multiple Subtitle' in info[2] or 'MultiSub' in info[2] or 'POR-BR' in info[2]:
                ep = dict()
                ep['eps'] = [info[1]]
                ep['links'] = [link]
                ep['extensao'] = ['.mkv']
                lista[info[0]] = ep
    else:
        if info[1] in lista[info[0]]['eps']:
            n = lista[info[0]]['eps'].index(info[1])
            if 'HEVC' in info[2]:
                if 'Multiple Subtitle' in info[2] or 'Multisub' in info[2] or 'POR-BR' in info[2]:
                    lista[info[0]]['links'][n] = link
        else:
            if 'HEVC' in info[2] or '1080p' in info[2]:
                if 'Multiple Subtitle' in info[2] or 'MultiSub' in info[2] or 'POR-BR' in info[2]:
                    lista[info[0]]['eps'].append(info[1])
                    lista[info[0]]['links'].append(link)
                    lista[info[0]]['extensao'].append('.mkv')
    return lista

def busca(pagina, lista=None):
    if lista == None:
        lista = dict()
    animes = pagina.find_class('success')
    for anime in animes:
        nome = anime.findall('.td[2]/a')[-1].get('title')
        try:
            info = extrair_nome(nome)
        except:
            continue
        if info != None:
            link = anime.find('.td[3]/a[2]').get('href')
            lista = filtrar(info, lista, link)
        else:
            continue
    return lista