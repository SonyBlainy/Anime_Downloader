from selenium import webdriver
from drivee import trat
from drivee import googledrive as gd
import os
import pickle
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from time import sleep as mimir
import tc.baixarep as baixaai
import requests
from lxml.html import fromstring
import base64

path = f"C:\\Users\\{os.getlogin()}\\Desktop\\animes\\"
save = "C:\\Users\\Micro\\AppData\\Local\\Anime_downloader\\"
ops = Options()
ops.add_argument('--blink-settings=imagesEnabled=false')
ops.add_argument('--log-level=10')
ops.add_argument('--headless')
ops.add_argument('--window-size=1366,768')
ops.add_argument('--disable-popup-blocking')
servico = Service()


def pesquisar(nome):
    link = 'https://www.animestc.net/animes/'
    api = 'https://api2.animestc.com/series'
    para = {'order': 'title', 'direction': 'asc', 'page': 1, 'type': 'series', 'search': nome}
    r = requests.get(api, params=para)
    animes = list()
    for anime in r.json()['data']:
        data = dict()
        data['nome'] = anime['title']
        data['link'] = link+anime['slug']
        animes.append(data)
    return animes

def episodios(anime):
    prote = 'https://protetor.animestc.xyz/link/'
    resulta= requests.get(anime['link'])
    resulta = resulta.content.decode(resulta.apparent_encoding)
    resulta = fromstring(resulta)
    r = resulta.get_element_by_id('__nuxt')
    r = r.xpath('following::script[1]')[0]
    r = r.text
    r = '{'.join(r.split('{')[2:])
    ids = []
    for i in r.split('id'):
        a = i.split(',')
        if a[0][0] == ':':
            n = a[0][1:]
            try:
                n = int(n)
            except:
                pass
            else:
                ids.append(n)
    ids = list(ids.__reversed__())
    eps = resulta.find_class('episodes')[0]
    eps = eps.find_class('tooltip-container')
    copia = eps.copy()
    nomes = []
    for nome in copia:
        nome = nome.find_class('episode-info-title')[1]
        nome = nome.find('a[2]').text
        nomes.append(nome)
    nomes = list(nomes.__reversed__())
    posi = []
    for posicao in eps:
        se = dict()
        posicao = posicao.find_class('episode-info-links')[0]
        posicao = posicao.xpath('a')
        sim = ['gofile', 'drive']
        for p in posicao:
            if p.text.strip() in sim:
                se[p.text.strip().capitalize()] = posicao.index(p)
        posi.append(se)
    posi = list(posi.__reversed__())
    eps = []
    for i in range(0, len(nomes)):
        ep = dict()
        ep['ep'] = nomes[i]
        links = dict()
        for l in posi:
            for key in list(l.keys()):
                if key == 'Gofile' or key == 'Drive':
                    frase = f'{str(ids[i])}/high/{l[key]}'
                    frase = frase.encode('ascii')
                    frase = base64.b64encode(frase)
                    frase = frase.decode('ascii')
                    frase = prote+frase
                    links[key] = frase
        ep['links'] = links
        eps.append(ep)
    anime['eps'] = eps
    print('='*30)
    for i, ep in enumerate(anime['eps']):
        print(f'[{i}] {ep["ep"]}')
    while True:
        try:
            esco = str(input('Escolha um episodio ou digite sair: '))
            esco = int(esco)
        except:
            if esco.upper() == 'SAIR':
                break
            else:
                if '-' in esco:
                    break
                print('Erro! Tente novamente')
        else:
            break
    if type(esco) == int:
        anime['ep'] = anime['eps'][esco]
        anime.pop('eps')
        ep = baixar(anime)
        while True:
            if ep['ep']['nome_link'] == 'Gofile':
                ep = gofile(ep)
                if ep['erro']:
                    print('Mudando para Drive')
                    ep = baixar(ep, True)
                else:
                    break
            elif ep['ep']['nome_link'] == 'Drive':
                ep = trat.tratar(ep)
                if ep['erro']:
                    ep.pop('erro')
                    print('Erro! Acesso não autorizado ao arquivo, mudando para Gofile')
                    ep = baixar(ep, True)
                else:
                    verifica(ep)
                    try:
                        gd.baixar(ep)
                    except:
                        ep.pop('erro')
                        print('Erro! Não foi possível baixar pelo Drive, mudando para Gofile')
                        ep['nome'] = ' '.join(ep['nome'].split('_'))
                        ep = baixar(ep, True)
                    else:
                        break
    else:
        if esco.upper() != 'SAIR':
            varios = [int(e) for e in esco.split('-')]
            anime['eps'] = [e for i, e in enumerate(anime['eps']) if i in varios]
            for e in anime['eps']:
                anime['ep'] = e
                ep = baixar(anime, varios=True)
                while True:
                    if ep['ep']['nome_link'] == 'Gofile':
                        ep = gofile(ep)
                        if ep['erro']:
                            print('Mudando para Drive')
                            ep = baixar(ep, True)
                        else:
                            break
                    elif ep['ep']['nome_link'] == 'Drive':
                        ep = trat.tratar(ep)
                        if ep['erro']:
                            ep.pop('erro')
                            print('Erro! Acesso não autorizado ao arquivo, mudando para Gofile')
                            ep = baixar(ep, True)
                        else:
                            verifica(ep)
                            try:
                                gd.baixar(ep)
                            except:
                                ep.pop('erro')
                                print('Erro! Não foi possível baixar pelo Drive, mudando para Gofile')
                                ep['nome'] = ' '.join(ep['nome'].split('_'))
                                ep = baixar(ep, True)
                            else:
                                break

def baixar(ep, mudando=False, varios=False):
    pega = 'https://protetor.animestc.xyz/api/link/'
    if not mudando:
        if not varios:
            for i, e in enumerate(ep['ep']['links']):
                print(f'[{i}] {e}')
            while True:
                try:
                    esco = str(input('Escolha de qual servidor deseja baixar ou digite sair: '))
                    esco = int(esco)
                except:
                    if esco.upper() == 'SAIR':
                        break
                    else:
                        print('Erro! Tente novamente')
                else:
                    if esco >= 0 and esco < len(ep['ep']['links']):
                        break
                    else:
                        print('Erro! Opção inválida')
        else:
            esco = [l for l in ep['ep']['links']]
            esco = esco.index('Drive')
        if type(esco) == int:
            nome = [k for k in ep['ep']['links']][esco]
            link = ep['ep']['links'][nome]
            r = requests.get(link)
            r = fromstring(r.content)
            linkid = r.get_element_by_id('link-id')
            linkid = linkid.get('value')
            while True:
                try:
                    link = requests.get(pega+str(linkid)).json()['link']
                except:
                    pass
                else:
                    break
    else:
        for n in ep['ep']['links']:
            if n != ep['ep']['nome_link']:
                esco = [i for i, c in enumerate(ep['ep']['links']) if c == n][0]
                nome = n
                link = ep['ep']['links'][nome]
                r = requests.get(link)
                r = fromstring(r.content)
                linkid = r.get_element_by_id('link-id')
                linkid = linkid.get('value')
                while True:
                    try:
                        link = requests.get(pega+str(linkid)).json()['link']
                    except:
                        pass
                    else:
                        break
                break
    if type(esco) == int:
        ep['ep']['ep_link'] = link
        ep['ep']['nome_link'] = nome
    return ep

def verifica(ep):
    nome = '_'.join(ep['nome'].split())
    if not os.path.isdir(path+nome):
        os.mkdir(path+nome)
    if not os.path.isdir(save+nome):
        os.mkdir(save+nome)
        with open(save+nome+'\\'+'linkzinho.txt', 'wb') as arquivo:
            ep_save = ep.copy()
            ep_save.pop('ep')
            pickle.dump(ep_save, arquivo)

def gofile(ep):
    with webdriver.Firefox(options=ops, service=servico) as navegador:
        navegador.get(ep['ep']['ep_link'])
        navegador.add_cookie({'name': 'accountToken', 'value': '9EV9xTdiDoQL334CBpB60nPe8K2Rcwtc'})
        navegador.refresh()
        mimir(5)
        try:
            link = navegador.find_element(By.CLASS_NAME, 'col-md')
            link = link.find_element(By.CLASS_NAME, 'dropdown-menu')
            link = link.find_element(By.TAG_NAME, 'a')
        except:
            print('Erro! Arquivo temporariamente indisponivel')
            ep['erro'] = True
            return ep
        else:
            sim = True
            nome = (link.get_attribute('href')).split('.')[-1]
            link = link.get_attribute('href')
            ep['ep']['ep_link'] = link
            limpo = ep['nome'].split()
            for i, palavra in enumerate(limpo):
                limpo[i] = ''.join([l for l in palavra if l not in [':', '?', '°']])
            limpo = ' '.join(limpo)
            ep['nome'] = limpo
            nome = '_'.join(ep['nome'].split())+'_'+'_'.join(ep['ep']['ep'].split())+'.'+nome
            ep['ep']['nome'] = nome
            ep['ep']['caminho'] = path+'_'.join(ep['nome'].split())+'\\'
            c = dict()
            cu = navegador.get_cookies()
            for i in cu:
                c[i['name']] = i['value']
            ep['ep']['cookie'] = c
            ep['erro'] = False
    if sim:
        verifica(ep)
        baixaai.baixarar(ep)
    return ep
