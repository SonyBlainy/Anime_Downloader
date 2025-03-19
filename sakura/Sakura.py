from selenium import webdriver
from drivee.core import Anime, Ep
import requests
from lxml.html import fromstring
from fera import baixando
from ouo_bypass import ouo_bypass
from selenium.webdriver.common.by import By
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import FirefoxService
from time import sleep as mimir

ops = FirefoxOptions()
ops.log.level = 'trace'
ops.add_argument('--blink-settings=imagesEnabled=false')
ops.add_argument('--headless')
ops.add_argument('--window-size=1366,768')
ops.add_argument('--disable-popup-blocking')
server = FirefoxService()

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
    print('[0] Pasta de Download')
    print('[1] Episodios Unicos')
    while True:
        try:
            esc = int(input('Digite sua escolha: '))
        except:
            print('Erro! Tente novamente')
        else:
            if esc in (0, 1):
                break
            else:
                print('Erro! Tente novamente')
    r = requests.get(anime.link)
    r = fromstring(r.content)
    r = r.find_class('tab-content')[0]
    if r.find('.div[@id="fhd"]').find('.table') != None:
        link = r.find('.div[@id="fhd"]')
    else:
        link = r.find('.div[@id="hd"]')
    if esc == 0:
        link = link.find('.table').find('.//td').xpath('a')
        for l in link:
            texto = l.xpath('text()')[1].strip()
            if texto == 'Mediafire':
                link = l.get('href')
                break
        try:
            link = fromstring(requests.get(link).content)
        except:
            return None
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
                    final = e['filename'].split('_')[-1]
                    if len(final.split('.')) > 2:
                        nome = 'Episodio'+'_'+'_'.join(final.split('.')[:-1])
                    else:
                        nome = 'Episodio'+'_'+final.split('.')[0]
            else:
                if e['filename'].split('_')[-2] == 'Final':
                    nome = 'Final'
                else:
                    nome = 'Episodio'+f'_{e["filename"].split("_")[-1].split()[0]}'
            estensao ='.'+e['filename'].split('.')[-1]
            server = 'Mediafire'
            ep = Ep(nome, link, estensao, server)
            resposta.append(ep)
    else:
        links = link.xpath('table')[1].xpath('tr')
        resposta = []
        for l in links:
            nome = 'Episodio_'+l.find('td').text.split()[-1]
            link = l.xpath('td')[1].xpath('a')
            for ll in link.copy():
                if ll.find('span').text.strip() == 'Mediafire':
                    link = ll.get('href')
                    break
            server = 'Mediafire'
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
            estensao ='.'+link.split('/')[-2].split('.')[-1]
            ep = Ep(nome, link, estensao, server)
            resposta.append(ep)
    return resposta

def mediafire(anime):
    r = fromstring(requests.get(anime.ep.link).content)
    link = r.get_element_by_id('download_link')
    link = link.xpath('a')[1].get('href')
    anime.ep.link = link
    baixando.baixarar(anime)
    
