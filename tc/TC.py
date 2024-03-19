from selenium import webdriver
import os
import pickle
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep as mimir
import tc.baixarep as baixaai

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
    with webdriver.Firefox(options=ops) as navegador:
        navegador.get('https://www.animestc.net/animes')
        acoes = ActionChains(navegador)
        busca = navegador.find_element(By.CLASS_NAME, 'anime-entry')
        busca = busca.find_element(By.TAG_NAME, 'input')
        acoes.send_keys_to_element(busca, nome).perform()
        acoes.send_keys_to_element(busca, Keys.ENTER).perform()
        mimir(4)
        busca = navegador.find_element(By.CLASS_NAME, 'anime-entry-container')
        busca = busca.find_elements(By.XPATH, '*')
        animes = list()
        for a in busca:
            data = dict()
            link = a.get_attribute('href')
            data['link'] = link
            data['nome'] = a.find_element(By.CLASS_NAME, 'anime-entry-figure').find_element(By.TAG_NAME, 'img').get_attribute('alt')
            animes.append(data)
    return animes

def episodios(anime):
    with webdriver.Firefox(options=ops, service=servico) as navegador:
        navegador.get(anime['link'])
        mimir(5)
        eps = navegador.find_element(By.CLASS_NAME, 'episodes').find_elements(By.CLASS_NAME, 'tooltip-container')
        resultado = list()
        for ep in eps:
            data = dict()
            ep = ep.find_element(By.CLASS_NAME, 'episode-info')
            data['ep'] = ep.find_element(By.CLASS_NAME, 'episode-info-title').find_elements(By.TAG_NAME, 'a')[1].text
            hd = ep.find_element(By.CLASS_NAME, 'episode-info-tabs').find_elements(By.TAG_NAME, 'a')
            for h in hd:
                if h.text.split()[0] == '1080p':
                    navegador.execute_script('arguments[0].scrollIntoView();', h)
                    navegador.execute_script('arguments[0].click();', h)
            links = [l for l in ep.find_element(By.CLASS_NAME, 'episode-info-links').find_elements(By.TAG_NAME, 'a')]
            for i, l in enumerate(links):
                links[i] = l.get_attribute('href')
            nomes = [n for n in ep.find_element(By.CLASS_NAME, 'episode-info-links').find_elements(By.TAG_NAME, 'a')]
            for i, n in enumerate(nomes):
                nomes[i] = n.text.split()[0]
            l = dict()
            for i, link in enumerate(links):
                l[nomes[i]] = link
            data['links'] = l
            resultado.append(data)
        navegador.quit()
        resultado = [resultado[n] for n in range(len(resultado)-1, -1, -1)]
        anime['eps'] = resultado
    return anime

def baixar(ep):
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
    if type(esco) == int:
        nome = [k for k in ep['ep']['links']][esco]
        link = ep['ep']['links'][nome]
        with webdriver.Firefox(options=ops) as navegador:
            navegador.get(link)
            mimir(8)
            link = navegador.find_element(By.CLASS_NAME, 'counter').find_element(By.TAG_NAME, 'a').get_attribute('href')
    ep['ep'].pop('links')
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
    with webdriver.Firefox(options=ops) as navegador:
        navegador.get(ep['ep']['ep_link'])
        navegador.add_cookie({'name': 'accountToken', 'value': '9EV9xTdiDoQL334CBpB60nPe8K2Rcwtc'})
        navegador.refresh()
        mimir(10)
        navegador.refresh()
        try:
            link = navegador.find_element(By.CLASS_NAME, 'col-md-auto')
            link = link.find_element(By.XPATH, '..')
            link = link.find_element(By.TAG_NAME, 'a')
        except:
            print('Erro! Arquivo temporariamente indisponivel')
            sim = False
        else:
            sim = True
            nome = link.text
            link = link.get_attribute('href')
            ep['ep']['ep_link'] = link
            limpo = ep['nome'].split()
            for i, palavra in enumerate(limpo):
                limpo[i] = ''.join([l for l in palavra if l not in [':', '?', '°']])
            limpo = ' '.join(limpo)
            ep['nome'] = limpo
            nome = nome.split()
            nome = nome[-1].split('.')[-1]
            nome = '_'.join(ep['nome'].split())+'_'+'_'.join(ep['ep']['ep'].split())+'.'+nome
            ep['ep']['nome'] = nome
            ep['ep'].pop('nome_link')
            ep['ep']['caminho'] = path+'_'.join(ep['nome'].split())+'\\'
            c = dict()
            cu = navegador.get_cookies()
            for i in cu:
                c[i['name']] = i['value']
            ep['ep']['cookie'] = c
    if sim:
        verifica(ep)
        baixaai.baixarar(ep)
