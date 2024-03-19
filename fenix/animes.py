from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import pickle
from fenix.baixando import baixarar
from fenix.renomear import reno
from fenix.rarzinho import descom
from time import sleep
import os

path = f"C:\\Users\\{os.getlogin()}\\Desktop\\animes\\"
save = "C:\\Users\\Micro\\AppData\\Local\\Anime_downloader\\"
ops = Options()
ops.add_experimental_option("excludeSwitches", ["enable-logging"])
ops.add_argument('--blink-settings=imagesEnabled=false')
ops.add_argument('--headless')
ops.add_argument('--window-size=1366,768')
ops.add_argument('--disable-popup-blocking')
server = Service(executable_path='chromedriver.exe')


def pesquisa():
    pesquisa_nome = str(input('Digite o nome do anime: '))
    with webdriver.Chrome(service=server, options=ops) as navegador:
        navegador.get('https://fenixfansub.net')
        busca = navegador.find_elements(By.CLASS_NAME, 'busca')[1]
        acoes = ActionChains(navegador)
        acoes.move_to_element(busca).click(busca).perform()
        sleep(1)
        busca = navegador.find_element(By.CLASS_NAME, 'proinput')
        busca = busca.find_element(By.TAG_NAME, 'input')
        busca.send_keys(pesquisa_nome)
        sleep(3)
        busca = navegador.find_elements(By.CLASS_NAME, 'resdrg')[1]
        busca = busca.find_elements(By.XPATH, '*')
        resultado = []
        for a in busca:
            data = dict()
            try:
                link = a.find_element(By.CLASS_NAME, 'asp_res_url').get_attribute('href')
            except:
                return []
            else:
                nome = a.find_element(By.CLASS_NAME, 'asp_res_url').text
                data['link'] = link
                data['nome'] = nome
                resultado.append(data)
        return resultado


def baixar(anime, principal=False):
    with webdriver.Chrome(service=server, options=ops) as navegador:
        if not os.path.isdir(save+'_'.join(anime['anime_nome'].split())):
            os.mkdir(save+'_'.join(anime['anime_nome'].split()))
            with open(save+'_'.join(anime['anime_nome'].split())+'\\linkzinho.txt', 'wb') as arquivo:
                pickle.dump(anime['link'], arquivo)
        if not os.path.isdir(path+'_'.join(anime['anime_nome'].split())):
            os.mkdir(path+'_'.join(anime['anime_nome'].split()))
        acoes = ActionChains(navegador)
        navegador.get(anime['link'])
        navegador.maximize_window()
        navegador.execute_script('scrollTo(0, document.body.scrollHeight)')
        testando = navegador.find_elements(By.CLASS_NAME, "nav-link")
        for t in testando:
            if t.get_attribute('href') == anime['link']+'#full':
                acoes.move_to_element(t).click(t).perform()
        sleep(5)
        sele = navegador.find_element(value='full').find_elements(By.XPATH, '*/*')[1:]
        if principal:
            if anime['varios']:
                eps = []
                for e in sele:
                    data = dict()
                    nome_ep = e.find_element(By.TAG_NAME, 'div').find_element(By.TAG_NAME, 'span')
                    if int(nome_ep.text.split()[1]) in anime['numero']:
                        busca = e.find_elements(By.TAG_NAME, 'a')
                        for l in busca:
                            if l.get_attribute('title') in 'mfire':
                                link = l.get_attribute('href')
                                data['link'] = link
                                data['ep'] = '_'.join(anime['anime_nome'].split())+'_'+'_'.join(nome_ep.text.split())
                                data['path'] = path+'_'.join(anime['anime_nome'].split())+'\\'
                                eps.append(data)
                zip(eps, True)
        else:
            for e in sele:
                nome_ep = e.find_element(By.TAG_NAME, 'div').find_element(By.TAG_NAME, 'span')
                if nome_ep.text.split()[1] in anime['numero']:
                    busca = e.find_elements(By.TAG_NAME, 'a')
                    for l in busca:
                        if l.get_attribute('title') == 'mfire':
                            link = l.get_attribute('href')
                            data = dict()
                            data['link'] = link
                            data['mega'] = False
                            data['ep'] = '_'.join(anime['anime_nome'].split())+'_'+'_'.join(nome_ep.text.split())
                            data['path'] = path+'_'.join(anime['anime_nome'].split())+'\\'
                        try:
                            data['t'] = 'teste'
                        except:
                            if l.get_attribute('title') == 'mega':
                                link = l.get_attribute('href')
                                data = dict()
                                data['link'] = link
                                data['mega'] = True
                                data['ep'] = '_'.join(anime['anime_nome'].split())+'_'+'_'.join(nome_ep.text.split())
                                data['path'] = path+'_'.join(anime['anime_nome'].split())+'\\'
            zip(data)


def zip(ep, varios=False):
    with webdriver.Chrome(service=server, options=ops) as navegador:
        if varios:
            for e in ep:
                navegador.get(e['link'])
                down = navegador.find_element(value='dlbutton')
                down = down.get_attribute('href')
                ep['link'] = down
                baixarar(ep['link'], ep['ep'], ep['path'])
                descom(ep['path']+ep['ep']+'.rar', ep['path'])
                reno(ep['path'], ep['ep']+'.mp4')
        else:
            if not ep['mega']:
                navegador.get(ep['link'])
                down = navegador.find_element(value='dlbutton')
                down = down.get_attribute('href')
                ep['link'] = down
                baixarar(ep['link'], ep['ep'], ep['path'])
                descom(ep['path']+ep['ep']+'.rar', ep['path'])
                reno(ep['path'], ep['ep']+'.mp4')
            else:
                while True:
                    try:
                        pass
                    except Exception as erro:
                        with open('erro.txt', 'w') as arquivo:
                            arquivo.write(f'{erro}')
                    else:
                        break
                descom(ep['path']+ep['ep']+'.rar', ep['path'])
                reno(ep['path'], ep['ep']+'.mp4')


def eps(anime):
    with webdriver.Chrome(service=server, options=ops) as navegador:
        acoes = ActionChains(navegador)
        navegador.get(anime['link'])
        testando = navegador.find_elements(By.CLASS_NAME, "nav-link")
        for t in testando:
            if t.get_attribute('href') == anime['link']+'#full':
                acoes.move_to_element(t).click(t).perform()
        sleep(5)
        episodios = navegador.find_element(By.ID, 'full').find_elements(By.XPATH, '*/*')[1:]
        resultados = []
        for e in episodios:
            data = dict()
            nome = anime['nome']
            link = anime['link']
            numero = e.find_element(By.TAG_NAME, 'span').text.split()[1]
            data['link'] = link
            data['anime_nome'] = nome
            data['numero'] = numero
            resultados.append(data)
        return resultados
    
    
def listar():
    for i, (caminho, diretorio, arquivo) in enumerate(os.walk(path)):
        if len(diretorio) > 0 and i == 0:
            for i, d in enumerate(diretorio):
                print(f'[{i}] {d}')
            while True:
                esc = str(input('Escolha um anime ou digite sair: '))
                try:
                    esc = int(esc)
                    esc = diretorio[esc]
                except:
                    if esc.upper() == 'SAIR':
                        break
                else:
                    break
        if esc == 'SAIR':
            break
        else:
            if caminho.split('\\')[-1] == esc:
                print('='*30)
                for i, a in enumerate(arquivo):
                    print(f'[{i}] {a}')
                while True:
                    esc = str(input('Escolha um episódio, digite sair ou baixar: '))
                    try:
                        esc = int(esc)
                    except:
                        if esc.upper() == 'SAIR':
                            break
                        elif esc.upper() == 'BAIXAR':
                            nome = caminho.split('\\')[-1]
                            try:
                                with open(save+nome+'\\'+'linkzinho.txt', 'rb') as arquivo:
                                    dados = pickle.load(arquivo)
                            except:
                                print('Erro! Arquivo não existe, baixe um episodio do anime para criar')
                            else:
                                if dados['link'].split('.')[1] == 'animestc':
                                    dados['site'] = 'TC'
                                elif 'sakuraanimes' in dados['link']:
                                    dados['site'] = 'Sakura'
                                return dados
                    else:
                        if 0 <= esc < len(arquivo):
                            os.popen(f'start {caminho}\\{arquivo[esc]}')
