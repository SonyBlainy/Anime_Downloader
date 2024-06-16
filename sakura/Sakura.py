from selenium import webdriver
import requests
from lxml.html import fromstring
from drivee.trat import tratar
from fera.animes_geral import verifica
from fera import baixando
import os
import pickle
from ouo_bypass import ouo_bypass
from selenium.webdriver.common.by import By
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import FirefoxService
from time import sleep as mimir
from sakura.baixarep import baixarar

ops = FirefoxOptions()
ops.log.level = 'trace'
ops.add_argument('--blink-settings=imagesEnabled=false')
ops.add_argument('--headless')
ops.add_argument('--window-size=1366,768')
ops.add_argument('--disable-popup-blocking')
server = FirefoxService()


class Anime:
    def __init__(self, nome, link):
        self.nome = nome
        self.link = link
    def eps(self):
        self.ep = listar_episodios(self)
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
            self.trat()
        else:
            self.ep = [self.ep[int(e)] for e in esco.split('-')]
    def trat(self):
        self = tratar(self, self.ep.estensao)
        verifica(self)
class Ep:
    def __init__(self, nome, link, estensao, server):
        self.nome = nome
        self.link = link
        self.estensao = estensao
        self.server = server


def pesquisar_anime(anime):
    with webdriver.Firefox(ops, server) as navegador:
        navegador.get('https://www.sakuraanimes.com')
        fecha = navegador.find_elements(By.CLASS_NAME, 'close')[-1]
        navegador.execute_script('arguments[0].click()', fecha)
        pesquisa = navegador.find_element(By.CLASS_NAME, 'mb-2')
        pesquisa.send_keys(anime)
        mimir(2)
        animes = navegador.find_element(value='myUL').find_elements(By.TAG_NAME, 'li')
        lista = []
        for anime in animes:
            link = anime.find_element(By.TAG_NAME, 'a')
            nome = link.text.strip()
            nome = nome.split('-')[0].strip()
            link = link.get_attribute('href')
            a = Anime(nome, link)
            lista.append(a)
    return lista
    
def listar_episodios(anime):
    api = 'https://www.mediafire.com/api/1.4/folder/get_content.php'
    r = requests.get(anime.link)
    r = fromstring(r.content)
    r = r.find_class('tab-content')[0]
    if r.find('.div[@id="fhd"]').find('.table') != None:
        link = r.find('.div[@id="fhd"]').find('.table').find('.//td')
    else:
        link = r.find('.div[@id="hd"]').find('.table').find('.//td')
    link = link.xpath('a')
    for l in link:
        texto = l.xpath('text()')[1].strip()
        if texto == 'Mediafire':
            link = l.get('href')
            break
    link = fromstring(requests.get(link).content)
    link = link.find_class('w-full')[0]
    link = link.find('a').get('href')
    contador = 0
    while True:
        try:
            link = ouo_bypass(link)['bypassed_link']
        except:
            contador += 1
            if contador == 10:
                return None
        else:
            break
    id = link.split('/')[4]
    para = {'content_type': 'files', 'filter': 'all', 'order_by': 'name', 'order_direction': 'asc', 'chunck': 1,
            'version': 1.5, 'folder_key': id, 'response_format': 'json'}
    r = requests.get(api, para)
    resposta = dict(r.json())
    eps = resposta['response']['folder_content']['files']
    resposta = []
    for e in eps:
        link = e['links']['normal_download']
        if len(e['filename'].split('_')[-1].split()) == 1:
            if e['filename'].split('_')[-2] == 'Final':
                nome = 'Episodio'+'_'+'_'.join(e['filename'].split('_')[-3:-1])
            else:
                nome = 'Episodio'+'_'+e['filename'].split('_')[-2]
        else:
            if e['filename'].split('_')[-2] == 'Final':
                nome = 'Final'
            else:
                nome = 'Episodio'+f'_{e["filename"].split("_")[-1].split()[0]}'
        estensao ='.'+e['filename'].split('.')[-1]
        server = 'Mediafire'
        ep = Ep(nome, link, estensao, server)
        resposta.append(ep)
    return resposta

def mediafire(anime):
    r = fromstring(requests.get(anime.ep.link).content)
    link = r.get_element_by_id('download_link')
    link = link.xpath('a')[1].get('href')
    anime.ep.link = link
    baixando.baixarar(anime)
    
