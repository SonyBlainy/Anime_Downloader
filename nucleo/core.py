from httpx import AsyncClient as Client
import navegador
import zipfile
import re
import json
from lxml.html import fromstring
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from infinite import infinete
from ferramentas import baixando
from sakura import Sakura
from erai import erai_animes, torrent
from bakashi import bakashi_anime
from random import randint
import logging
import pickle
import os
import sys
import subprocess
import shutil
import asyncio
import cv2
from customtkinter import CTkLabel, CTkFrame
from PIL import Image

path = os.getenv('caminho')
save = os.getenv('save')

class Anime:
    def __init__(self, nome, link, imagem, ep=None):
        self.nome_pesquisa = None
        self.nome = nome
        self.nome_pesquisa = None
        self.caminho = None
        self.link = link
        self.ep = ep
        self.imagem = imagem
        self.info = None
        self.tratar_nome()

    def tratar_nome(self):
        lista_negra = [':', '°', '?', '-', ',', '“', '”', '.', '\\', '/']
        limpo = ' '.join([''.join([letra for letra in palavra if letra not in lista_negra]) for palavra in self.nome.split()])
        self.nome_pesquisa = self.nome
        self.nome = limpo
        logging.info(f'Nome do anime {limpo} tratado')

    def verifica(self):
        nome = '_'.join(self.nome.split())
        anime_path = os.path.join(path, nome)
        self.caminho = anime_path
        save_path = os.path.join(save, nome)
        for d in (anime_path, save_path):
            os.makedirs(d, exist_ok=True)
        save_file = os.path.join(save_path, 'save.pkl')
        if not os.path.isfile(save_file):
            try:
                with open(save_file, 'wb') as arquivo:
                    pickle.dump(self, arquivo)
                logging.info(f'Arquivo save criado para o anime {nome}')
            except OSError as e:
                logging.error(f'Erro ao criar save para o anime {nome}: {e}')

class Ep:
    def __init__(self, nome, link, estensao=None, server=None):
        self.nome = nome
        self.link = link
        self.estensao = estensao
        self.server = server
        self.caminho = None

def divisor(lista, tamanho=5):
    for i in range(0, len(lista), tamanho):
        yield lista[i:i+tamanho]

async def pesquisar_tudo(nome:str):
    try:
        erai = await erai_animes.pesquisar(nome)
    except:
        logging.exception('Erro ao obter animes de erai')
        erai = None
    sakura = None
    q1n = None
    dados = {'Erai': erai, 'Sakura': sakura, 'Q1n': q1n}
    for chave in dados.keys():
        if dados[chave]:
            dados[chave] = [Anime(anime['nome'], anime['link'], anime['imagem']) for anime in dados[chave]]
    return dados

async def anime_info_pesquisa(anime):
    api = 'https://api.myanimelist.net/v2'
    client_id = 'a81a1ee7e886f2f0c54ec850594667a3'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'}
    header_mal = {'X-MAL-CLIENT-ID': client_id}
    infos = ['title', 'start_date', 'end_date', 'mean', 'status', 'genres', 'num_episodes',
             'start_season', 'broadcast', 'source', 'related_anime', 'related_manga', 'synopsis']
    if 'erai-raws' in anime.link:
        async with Client(headers=header, cookies=json.load(open('cookies.json'))) as client:
            pagina = await client.get(anime.link)
            pagina = fromstring(pagina.content)
            anime_id = pagina.find_class('entry-content')[0].find_class('entry-content-buttons')[-2]
            anime_id = anime_id.findall('a')[-1].get('href')
            anime_id = re.findall(r'anime/(.*)', anime_id)[0]
    async with Client(headers=header_mal, params={'fields': ','.join(infos)}) as client:
        anime_info = await client.get(api+f'/anime/{anime_id}')
        anime.info = anime_info.json()
    return anime
    
async def escolher_ep_erai(anime: Anime):
    eps = await erai_animes.extrair_ep(anime.link)
    eps_list = [Ep(f'Episódio {e}', eps[e]) for e in eps.keys()]
    return eps_list
        
def escolher_anime_sakura(nome=None, animes=None, baixar=False):
    pass

def escolher_anime_bakashi(nome=None, animes=None, baixar=False):
    pass

def escolher_animes_infinite(nome=None, animes=None, baixar=False):
    pass
    
def data_info(broadcast):
    dia = broadcast['day_of_the_week']
    hora = broadcast['start_time']
    dias_da_semana = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thurday': 3,
                      'Friday': 4, 'Saturday': 5, 'Sunday': 6}
    dia_esperado = dias_da_semana[dia.capitalize()]
    time = datetime.strptime(hora, '%H:%M').time()
    now_jst = datetime.now(ZoneInfo('Asia/Tokyo'))
    hj_jst = now_jst.date()
    dia_s_jst = hj_jst.weekday()
    days_ahead = (dia_esperado-dia_s_jst)%7
    if days_ahead == 0 and now_jst.time() > time:
        days_ahead = 7
    dia_alvo = hj_jst + timedelta(days_ahead)
    dt_jst = datetime.combine(dia_alvo, time).replace(tzinfo=ZoneInfo('Asia/Tokyo'))
    data = dt_jst.astimezone(ZoneInfo('America/Sao_Paulo'))
    return {'dia': data.strftime('%A'), 'hora': data.strftime('%H:%M')}

async def selecionar_ep(anime: Anime):
    eps = {'erai-raws': escolher_ep_erai}
    anime.ep = await eps[re.findall(r'\.(.*)\.', anime.link)[0]](anime)
    return anime

async def baixar_ep_erai(ep: Ep):
    qbit = torrent.Qbit()
    await qbit.init_sessao()
    if qbit.sessao:
        await qbit.baixar(ep)

def anime_info(anime_caminho):
    arquivos = os.listdir(anime_caminho)
    if len(arquivos) > 1:
        caminho = arquivos[1]
    else:
        caminho = arquivos[0]
    with open(os.path.join(anime_caminho, caminho), 'rb') as arquivo:
        return pickle.load(arquivo)

def listar_anime():
    result = []
    with os.scandir(save) as i:
        for a in i:
            infos = anime_info(a.path)
            if os.path.exists(infos.caminho):
                result.append(infos)
            else:
                shutil.rmtree(a.path)
    return result

def listar_ep(anime: Anime):
    arquivos = []
    if anime.caminho:
        with os.scandir(anime.caminho) as i:
            for a in i:
                arquivos.append(a)
        if arquivos:
            return arquivos
        else:
            return None
    else:
        return None

async def update(versao):
    link = 'https://api.github.com/repos/SonyBlainy/Anime_Downloader/releases/latest'
    async with Client() as client:
        r = await client.get(link)
        data = r.json()
        if data['tag_name'] != versao:
            link = data['assets'][0]['browser_download_url']
            caminho = os.path.expandvars(r'%temp%\anime_downloader_temp')
            os.makedirs(caminho, exist_ok=True)
            caminho = os.path.join(caminho, 'instalador.exe')
            subprocess.run(['powershell', '-NoProfile', '-Command', 'wget', link, '-UseBasicParsing',
                            '-O', caminho], encoding='utf-8')
            os.startfile(caminho)
    sys.exit()

def abrir_pasta(caminho: str):
    subprocess.run(['powershell', '-NoProfile', '-Command', 'explorer', caminho],
                   encoding='utf-8',
                   creationflags=subprocess.CREATE_NO_WINDOW)
    
def deletar_anime(caminho: str):
    shutil.rmtree(caminho)

def fechar():
    pass

async def torrent_info():
    qbit = torrent.Qbit()
    await qbit.init_sessao()
    info = await qbit.infos()
    animes = {}
    for i in info:
        try:
            nome = i['name']
            if re.findall(r'(\[Erai-raws\]) ', nome)[0]:
                anime_nome = os.path.split(i['save_path'])[-1]
                anime = pickle.load(open(os.path.join(save, os.path.split(i['save_path'])[-1], 'save.pkl'), 'rb'))
                if anime_nome not in animes.keys():
                    animes[anime_nome] = {'anime': anime, 'hashs': [i['hash']]}
                else:
                    animes[anime_nome]['hashs'].append(i['hash'])
        except:
            logging.exception('Erro ao obter downloads')
    return animes

def gerar_frames(anime: Anime, anime_path: str):
    eps = listar_ep(anime)
    lista_frames = []
    for ep in eps:
        frames_ep = []
        try:
            video = cv2.VideoCapture(ep.path)
            if not video.isOpened():
                raise OSError('Arquivo não abre')
            frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            if frames < 100:
                raise ValueError('Arquivo provavelmente corrompido')
            n = randint(10, frames-1)
            video.set(cv2.CAP_PROP_POS_FRAMES, n)
            ok, frame = video.read()
            if not ok:
                raise ValueError('Erro ao ler o frame')
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
        except OSError:
            logging.warning(f'Erro ao abrir o arquivo {ep.name}, pulando episódio')
        except:
            logging.warning(f'Erro no arquivo {ep.name}')
        else:
            tamanho = (int(frame.width/4), int(frame.height/4))
            frame = frame.resize(tamanho)
            frames_ep.append(frame)
            for _ in range(4):
                n = randint(10, frames-1)
                video.set(cv2.CAP_PROP_POS_FRAMES, n)
                ok, frame = video.read()
                if ok:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = Image.fromarray(frame)
                    frame = frame.resize(tamanho)
                    frames_ep.append(frame)
        finally:
            if 'video' in locals():
                video.release()
        lista_frames.append(frames_ep)
    with open(os.path.join(anime_path, 'frames.pkl'), 'wb') as arquivo:
        pickle.dump(lista_frames, arquivo)

def carregar_frames(frame_path: str):
    with open(os.path.join(frame_path, 'frames.pkl'), 'rb') as arquivo:
        return pickle.load(arquivo)

def label_log(frame: CTkFrame, texto: str):
    label = CTkLabel(frame, text=texto, font=('Arial', 15))
    return label

def deletar_frames(anime_caminho):
    anime_caminho = os.path.join(save, os.path.split(anime_caminho)[-1])
    with os.scandir(anime_caminho) as i:
        for arquivo in i:
            if arquivo.name == 'frames.pkl':
                os.remove(arquivo.path)

async def obter_cookies():
    cookies = await navegador.cookies()
    lista_cookies = [{i['name']: i['value']} for i in cookies if 'wordpress_logged_in' in i['name']][0]
    with open('cookies.json', 'w') as arquivo:
        json.dump(lista_cookies, arquivo, indent=4)

def verificar_navegador():
    if not os.path.exists(r'.\chrome-win64'):
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        link = 'https://cdn.playwright.dev/builds/cft/147.0.7727.15/win64/chrome-win64.zip'
        subprocess.run(['powershell', '-NoProfile', '-Command', 'curl.exe', '-L', '--progress-bar',
                        '-A', f'"{user_agent}"', '-o', 'chrome.zip', f'"{link}"'])
        with zipfile.ZipFile('chrome.zip') as arquivo:
            arquivo.extractall('.')
        os.remove('chrome.zip')

async def verifica_cookies():
    cookie = json.load(open('cookies.json'))
    for a in cookie.keys():
        if 'wordpress_logged_in' in a:
            return
    await obter_cookies()
