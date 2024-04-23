from selenium import webdriver
from drivee.trat import tratar
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


class Anime:
    def __init__(self, nome, link):
        self.nome = nome
        self.link = link
    def ep(self):
        self.ep = episodios(self)
    def listar(self):
        print('='*30)
        for i, ep in enumerate(self.ep):
            print(f'[{i}] {ep.nome}')
        while True:
            try:
                esco = str(input('Escolha qual episódio deseja baixar: '))
                esco = int(esco)
            except:
                if esco.upper() == 'SAIR':
                    break
                elif '-' in esco:
                    break
                else:
                    print('Erro! Tente novamente')
            else:
                if esco >= 0 and esco <= len(self.ep)-1:
                    break
                else:
                    print('Erro! Tente novamente')
        if type(esco) == int:
            self.ep = self.ep[esco]
        else:
            if '-' in esco:
                esco = [int(i) for i in esco.split('-')]
                self.ep = [ep for ep in self.ep if self.ep.index(ep) in esco]
            else:
                self.ep = None
    def verificar(self):
        verifica(self)
    def baixar(self):
        if self.ep.server == 'Drive':
            self = tratar(self)
            if self.ep.erro:
                print('Erro! Mundando para Gofile')
                self.ep.server = 'Gofile'
            else:
                try:
                    gd.baixar(self.ep)
                except:
                    print('Erro ao baixar, mundando para Gofile')
                    self.ep.server = 'Gofile'
        if self.ep.server == 'Gofile':
            pass
        
class Ep:
    def __init__(self, ep):
        self.nome = ep['ep']
        self.links = ep['links']
        self.link = None
        self.server = None
        self.caminho = None
        self.erro = None

def pesquisar(nome):
    l = 'https://www.animestc.net/animes/'
    api = 'https://api2.animestc.com/series'
    para = {'order': 'title', 'direction': 'asc', 'page': 1, 'type': 'series', 'search': nome}
    r = requests.get(api, params=para)
    animes = list()
    for anime in r.json()['data']:
        n = anime['title']
        link = l+anime['slug']
        a = Anime(n, link)
        animes.append(a)
    return animes

def episodios(anime):
    prote = 'https://protetor.animestc.xyz/link/'
    resulta= requests.get(anime.link)
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
        azinho = posicao.find_class('episode-info-links')[0]
        azinho = azinho.xpath('a')
        sim = ['gofile', 'drive']
        for p in azinho:
            if p.text.strip() in sim:
                se[p.text.strip().capitalize()] = azinho.index(p)
        posi.append(se)
    posi = list(posi.__reversed__())
    eps = []
    for i in range(0, len(nomes)):
        ep = dict()
        ep['ep'] = nomes[i]
        links = dict()
        for f in posi[i].keys():
            frase = f'{str(ids[i])}/high/{posi[i][f]}'
            frase = frase.encode('ascii')
            frase = base64.b64encode(frase)
            frase = frase.decode('ascii')
            frase = prote+frase
            links[f] = frase
        ep['links'] = links
        e = Ep(ep)
        eps.append(e)
    return eps
  
def baixar(ep, mudando=False, varios=False):
    pega = 'https://protetor.animestc.xyz/api/link/'
    if not mudando:
        if not varios:
            for i, e in enumerate(ep.links):
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
                    if esco >= 0 and esco < len(ep.links):
                        break
                    else:
                        print('Erro! Opção inválida')
        else:
            esco = [l for l in ep.links]
            esco = esco.index('Drive')
        if type(esco) == int:
            nome = [k for k in ep.links][esco]
            link = ep.links[nome]
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
        for n in ep.links:
            if n != ep.server:
                esco = [i for i, c in enumerate(ep.links) if c == n][0]
                nome = n
                link = ep.links[nome]
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
        ep.link = link
        ep.server = nome
    return ep

def verifica(anime):
    nome = '_'.join(anime.nome.split())
    if not os.path.isdir(path+nome):
        os.mkdir(path+nome)
    if not os.path.isdir(save+nome):
        os.mkdir(save+nome)
        with open(save+nome+'\\'+'linkzinho.txt', 'wb') as arquivo:
            anime.ep = None
            pickle.dump(anime, arquivo)

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
