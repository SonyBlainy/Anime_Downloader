import requests
import re
from lxml.html import fromstring
import os
save = os.getenv('save')
path = os.getenv('caminho')

def pesquisar(nome:str):
    if len(nome.split()) > 1:
        nome = '+'.join(nome.split())
    api = 'https://nyaa.land/user/Erai-raws'
    post = {'f':0, 'c':'0_0', 'q':nome}
    r = fromstring(requests.get(api, post).content)
    page = r.find_class('center')[0].find_class('pagination')
    if len(page) > 0:
        resultado = busca(r)
        while True:
            page = r.find_class('center')[0].find_class('pagination')
            if len(page) > 0:
                print(page)
                page = page[0]
                try:
                    link = 'https://nyaa.land'+page.find_class('next')[0].find('a').get('href')
                except:
                    break
                else:
                    r = fromstring(requests.get(link).content)
                    resultado = busca(r, resultado)
    else:
        resultado = busca(r)
    return resultado

def busca(pagina, lista=None):
    if lista == None:
        lista = dict()
    animes = pagina.find_class('success')
    for anime in animes:
        if anime.find('.td[2]/a[2]') == None:
            nome = anime.find('.td[2]/a').get('title')
        else:
            nome = anime.find('.td[2]/a[2]').get('title')
        anime_nome = ' '.join(nome.split('-')[1].split()[1:])
        n = nome.split('-')[2].split()[0]
        colchetes = re.findall(r'\[(.*?)\]', nome)
        link = anime.find('.td[3]/a[2]').get('href')
        if lista.get(anime_nome) == None:
            if '1080p' in colchetes or 'HEVC' in colchetes and 'POR-BR' in colchetes:
                ep = dict()
                ep['eps'] = [n]
                ep['links'] = [link]
                ep['extensao'] = ['.mkv']
                lista[anime_nome] = ep
        else:
            if n in lista[anime_nome]['eps'] and 'HEVC' in colchetes and 'POR-BR' in colchetes:
                numero = lista[anime_nome]['eps'].index(n)
                lista[anime_nome]['links'][numero] = link
                lista[anime_nome]['extensao'][numero] = '.mkv'
            elif '1080p' in colchetes and 'POR-BR' in colchetes and n not in lista[anime_nome]['eps']:
                lista[anime_nome]['eps'].append(n)
                lista[anime_nome]['links'].append(link)
                lista[anime_nome]['extensao'].append('.mkv')
    return lista