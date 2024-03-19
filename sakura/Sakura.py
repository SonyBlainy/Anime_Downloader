from selenium import webdriver
import os
import pickle
from ouo_bypass import ouo_bypass
from sakura.uloz import linkzinho
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


def pesquisar_anime():
    anime = str(input('Digite o nome do anime: '))
    with webdriver.Firefox(service=server, options=ops) as navegador:
        navegador.get('https://www.sakuraanimes.com')
        acoes = ActionChains(navegador)
        mimir(1)
        fecha = navegador.find_elements(By.CLASS_NAME, 'm-0')[3]
        fecha = fecha.find_element(By.CLASS_NAME, 'close')
        fecha.click()
        bara = navegador.find_element(By.CLASS_NAME, 'mb-2')
        acoes.move_to_element(bara).click(bara).send_keys(anime).perform()
        mimir(3.5)
        busca = navegador.find_element(By.ID, 'myUL')
        acoes.move_to_element(busca).perform()
        busca = busca.find_elements(By.TAG_NAME, 'li')
        animes = list()
        for a in busca:
            data = dict()
            link = a.find_element(By.TAG_NAME, 'a').get_attribute('href')
            nome = a.find_element(By.TAG_NAME, 'a').text
            nome = nome.split()
            if nome[-1] != 'Legendados' and nome[-1] != 'Actions':
                nome = ' '.join(nome[:-2])
            else:
                nome = ' '.join(nome[:-3])
            data['link'] = link
            data['nome'] = nome
            animes.append(data)
        return animes
    
def listar_episodios(anime):
    with webdriver.Firefox(service=server, options=ops) as navegador:
        acoes = ActionChains(navegador)
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
        acoes.move_to_element(hd).click(hd).perform()
        mimir(2)
        links = navegador.find_elements(By.CLASS_NAME, 'table-dark')[-1].find_element(By.TAG_NAME, 'td').find_elements(By.TAG_NAME, 'a')
        for i, l in enumerate(links):
            print(f'[{i}] {l.text.split()[0]}')
        while True:
            try:
                pla = int(input('Escolha em qual plataforma deseja baixar: '))
            except:
                print('Erro! Tente novamente')
            else:
                if pla >= 0 and pla < len(links):
                    break
                else:
                    print('Erro! Opção inválida')
        if links[pla].text.split()[0] == 'Uloz':
            link = links[pla].get_attribute('href')
            navegador.get(link)
            mimir(4)
            link = navegador.find_element(By.CLASS_NAME, 'w-full').find_element(By.TAG_NAME, 'a')
            while True:
                try:
                    link = ouo_bypass(link.get_attribute('href'))['bypassed_link']
                except KeyboardInterrupt:
                    break
                except Exception as erro:
                    print(erro)
                else:
                    break
            anime['ep'] = linkzinho(link)
        elif links[pla].text.split()[0] == 'Mediafire':
            link = links[pla].get_attribute('href')
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
            for i, ep in enumerate(episodios):
                episodios[i] = mediafire(ep)
            anime['ep'] = episodios
    return anime

def baixar(anime):
    if not os.path.isdir(save+'_'.join(anime['nome'].split())):
        os.mkdir(save+'_'.join(anime['nome'].split()))
        with open(save+'_'.join(anime['nome'].split())+'\\linkzinho.txt', 'wb') as arquivo:
            copia = anime.copy()
            copia.pop('ep')
            pickle.dump(copia, arquivo)
    if anime['ep']['plataforma'] == 'Uloz':
        if not os.path.isdir(path+'_'.join(anime['nome'].split())):
            os.mkdir(path+'_'.join(anime['nome'].split()))
        caminho = path+'_'.join(anime['nome'].split())+'\\'
        baixarar(anime['ep']['link'], anime['ep']['nome'], caminho, anime['ep']['plataforma'], anime['ep']['cookie'])
    elif anime['ep']['plataforma'] == 'Mediafire':
        if not os.path.isdir(path+'_'.join(anime['nome'].split())):
            os.mkdir(path+'_'.join(anime['nome'].split()))
        caminho = path+'_'.join(anime['nome'].split())+'\\'
        baixarar(anime['ep']['link'], anime['ep']['nome'], caminho, anime['ep']['plataforma'])
      
def mediafire(ep):
    with webdriver.Firefox(service=server, options=ops) as navegador:
        navegador.get(ep['link'])
        mimir(3)
        link = navegador.find_element(value='download_link').find_elements(By.TAG_NAME, 'a')[1]
        link = link.get_attribute('href')
        ep['link'] = link
        return ep
    