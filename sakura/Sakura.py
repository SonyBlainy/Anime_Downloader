from selenium import webdriver
import requests
from lxml.html import fromstring
import os
import pickle
from ouo_bypass import ouo_bypass
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep as mimir
from sakura.baixarep import baixarar

path = f"C:\\Users\\{os.getlogin()}\\Desktop\\animes\\"
save = "C:\\Users\\Micro\\AppData\\Local\\Anime_downloader\\"
ops = Options()
ops.add_argument('--blink-settings=imagesEnabled=false')
ops.add_argument('--headless')
ops.add_argument('--window-size=1366,768')
ops.add_argument('--disable-popup-blocking')
server = Service()


class Anime:
    def __init__(self, nome, link):
        self.nome = nome
        self.link = link
    def eps(self):
        pass
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

def pesquisar_anime(anime):
    api = 'https://fenixfansub.net/wp-admin/admin-ajax.php'
    data = {'action': 'ajaxsearchpro_search', 'aspp': anime, 'asid': 2, 'asp_inst_id': '2_1'}
    r = requests.post(api, data)
    print(r.apparent_encoding)
    r = r.content.decode('utf-8')
    r = fromstring(r)
    animes = r.find_class('asp_content')
    for anime in animes:
        link = anime.xpath('.//a')[1]
        nome = link.text.strip()
        link = link.get('href')
        print(nome)
        print(link)
    
def listar_episodios(anime):
    with webdriver.Firefox(service=server, options=ops) as navegador:
        navegador.get(anime['link'])
        mimir(1)
        fecha = navegador.find_elements(By.CLASS_NAME, 'm-0')[-1]
        fecha = fecha.find_element(By.CLASS_NAME, 'close')
        fecha.click()
        hd = navegador.find_elements(By.TAG_NAME, 'ul')
        for i in hd:
            if i.get_attribute('role') == 'tablist':
                hd = i
                break
        hd = hd.find_elements(By.TAG_NAME, 'li')
        for ind, i in enumerate(hd):
            print(f'[{ind}] {i.find_element(By.TAG_NAME, "a").text}')
        while True:
            try:
                esco = int(input('Escolha qual qualidade deseja baixar: '))
            except:
                print('Erro! Tente novamente')
            else:
                if esco >= 0 and esco < len(hd):
                    break
        hd = hd[esco].find_element(By.TAG_NAME, 'a')
        navegador.execute_script('arguments[0].scrollIntoView();', hd)
        navegador.execute_script('arguments[0].click();', hd)
        mimir(1.5)
        links = navegador.find_elements(By.CLASS_NAME, 'table-dark')[-1].find_element(By.TAG_NAME, 'td').find_elements(By.TAG_NAME, 'a')
        servers = [l.text.split()[0] for l in links]
        if 'Mediafire' in servers:
            link = links[servers.index('Mediafire')].get_attribute('href')
            navegador.get(link)
            link = navegador.find_element(By.CLASS_NAME, 'w-full').find_element(By.TAG_NAME, 'a')
            while True:
                try:
                    link = ouo_bypass(link.get_attribute('href'))['bypassed_link']
                except KeyboardInterrupt:
                    exit()
                except Exception as erro:
                    print('Erro!')
                    print(f'{erro}')
                else:
                    break
            try:
                navegador.get(link)
            except:
                print(link)
            anime['link'] = link
            mimir(8)
            eps = navegador.find_element(value='main_list')
            eps = eps.find_elements(By.TAG_NAME, 'li')
            episodios = list()
            for e in eps:
                data = dict()
                link = e.find_element(By.TAG_NAME, 'a').get_attribute('href')
                nome = e.find_element(By.CLASS_NAME, 'item-name').text
                data['link'] = link
                data['nome'] = nome
                data['plataforma'] = 'Mediafire'
                episodios.append(data)
    anime['ep'] = mediafire(episodios)
    return anime

def baixar(anime):
    if not os.path.isdir(save+'_'.join(anime['nome'].split())):
        os.mkdir(save+'_'.join(anime['nome'].split()))
        with open(save+'_'.join(anime['nome'].split())+'\\linkzinho.txt', 'wb') as arquivo:
            copia = anime.copy()
            copia.pop('ep')
            pickle.dump(copia, arquivo)
    if anime['ep']['plataforma'] == 'Mediafire':
        if not os.path.isdir(path+'_'.join(anime['nome'].split())):
            os.mkdir(path+'_'.join(anime['nome'].split()))
        caminho = path+'_'.join(anime['nome'].split())+'\\'
        baixarar(anime['ep']['link'], anime['ep']['nome'], caminho, anime['ep']['plataforma'])
      
def mediafire(eps):
    with webdriver.Firefox(service=server, options=ops) as navegador:
        resul = []
        for ep in eps:
            navegador.get(ep['link'])
            mimir(3)
            link = navegador.find_element(value='download_link').find_elements(By.TAG_NAME, 'a')[1]
            link = link.get_attribute('href')
            ep['link'] = link
            resul.append(ep)
    return resul
