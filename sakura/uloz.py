from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from time import sleep as mimir

ser = Service(executable_path='chromedriver.exe')
ops = Options()
ops.add_experimental_option("excludeSwitches", ["enable-logging"])
ops.add_argument('--blink-settings=imagesEnabled=false')
ops.add_argument('--headless')
ops.add_argument('--window-size=1366,768')
ops.add_argument('--disable-popup-blocking')


def login():
    with webdriver.Chrome(service=ser, options=ops) as navegador:
        acoes = ActionChains(navegador)
        navegador.get('https://ulozto.net/')
        log = navegador.find_element(By.CLASS_NAME, 't-header-login')
        acoes.click(log).perform()
        mimir(5)
        user = navegador.find_elements(By.TAG_NAME, 'input')
        senha = user.copy()
        user = [u for u in user if u.get_attribute('name') == 'username'][0]
        senha = [s for s in senha if s.get_attribute('name') == 'password'][0]
        user.send_keys('SonyBlainy')
        senha.send_keys('Rebeca1103')
        senha.send_keys(Keys.ENTER)
        mimir(3)
        cookies = list()
        for c in navegador.get_cookies():
            cookies.append({'name': c['name'], 'value': c['value']})
        return cookies

def linkzinho(link):
    cookie = login()
    with webdriver.Chrome(service=ser, options=ops) as navegador:
        acoes = ActionChains(navegador)
        navegador.get(link)
        mimir(3)
        for c in cookie:
            navegador.add_cookie(c)
        navegador.refresh()
        mimir(5)
        teste = navegador.find_elements(By.CLASS_NAME, 'ar-navigation-menu')[-1]
        acoes.click(teste.find_element(By.TAG_NAME, 'button')).perform()
        nome = teste.find_element(By.TAG_NAME, 'div')
        for i in nome.find_elements(By.TAG_NAME, 'button'):
            if i.text.split()[0] == 'Name':
                acoes.click(i).perform()
                break
        mimir(5)
        items = navegador.find_element(By.CLASS_NAME, 'ar-files-box').find_elements(By.XPATH, 'div')
        episodios = []
        for ep in items:
            data = dict()
            ep = ep.find_element(By.XPATH, '*')
            data['nome'] = ep.find_element(By.CLASS_NAME, 'name').find_element(By.TAG_NAME, 'h2').get_attribute('title')
            link = ep.find_element(By.CLASS_NAME, 'controls').find_element(By.XPATH, '*')
            link = link.find_element(By.CLASS_NAME , 'tools').find_element(By.TAG_NAME, 'a').get_attribute('href')
            data['link'] = link
            data['plataforma'] = 'Uloz'
            novo = dict()
            for c in cookie:
                novo[c['name']] = c['value']
            data['cookie'] = novo
            episodios.append(data)
    return episodios
