import requests
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from time import sleep
from tqdm.auto import tqdm


ops = Options()
ops.add_experimental_option("excludeSwitches", ["enable-logging"])
ops.add_argument('--blink-settings=imagesEnabled=false')
ops.add_argument('--headless')
ops.add_argument('--window-size=1366,768')
ops.add_argument('--disable-popup-blocking')
server = Service(executable_path='chromedriver.exe')

def baixarar(ep):
    cabeca = {'Accept-Encoding': '*', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    cookiee = ep['ep']['cookie']
    with webdriver.Chrome(service=server, options=ops) as navegador:
        navegador.get(ep['ep']['ep_link'])
        sleep(5)
        for i in cookiee:
            navegador.add_cookie({'name': i, 'value': cookiee[i]})
        navegador.refresh()
        sleep(5)
        c = dict()
        for i in navegador.get_cookies():
            c[i['name']] = i['value']
    with requests.get(ep['ep']['ep_link'], stream=True, headers=cabeca, cookies=c, allow_redirects=False) as arquivo:
        total = int(arquivo.headers.get('Content-Length'))
        with tqdm.wrapattr(arquivo.raw, 'read', total) as raw:
            with open(ep['ep']['caminho']+ep['ep']['nome'], 'wb') as f:
                shutil.copyfileobj(raw, f)
