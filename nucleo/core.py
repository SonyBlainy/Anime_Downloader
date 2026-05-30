from httpx import AsyncClient as Client
import navegador
import zipfile
import re
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from erai import erai_animes, torrent
from erai.erai_animes import ErroCookie
from random import randint
import logging
import pickle
import os
import sys
import subprocess
import shutil
import asyncio
from customtkinter import CTkLabel, CTkFrame
from PIL import Image
import pandas as pd
import pickle

path = os.getenv('caminho')

def divisor(lista, tamanho=5):
    for i in range(0, len(lista), tamanho):
        yield lista[i:i+tamanho]

async def pesquisa_info(anime:dict) -> dict:
    anime['info'] = await anime_info_pesquisa(anime['id'])
    link = anime['info']['main_picture']['large']
    async with Client() as client:
        pagina = await client.get(link)
        imagem = pagina.content
    anime['imagem'] = imagem
    lista_negra = [':', '°', '?', '-', ',', '“', '”', '.', '\\', '/']
    limpo = ' '.join([''.join([letra for letra in palavra if letra not in lista_negra]) for palavra in anime['nome'].split()])
    anime['nome_pesquisa'] = anime['nome']
    anime['nome'] = limpo
    logging.info(f'Nome do anime {limpo} tratado')
    return anime

def series(anime:dict) -> pd.Series:
    anime = pd.Series(anime, name=anime['nome'])
    anime = anime.drop('nome')
    return anime

async def pesquisar(nome:str):
    while True:
        try:
            erai = await erai_animes.pesquisar(nome)
            lista = [pesquisa_info(a) for a in erai]
            resultado = []
            for chunck in divisor(lista):
                c = await asyncio.gather(*chunck)
                resultado.extend(c)
        except ErroCookie:
            await obter_cookies()
            continue
        except:
            logging.warning('Erro ao obter animes de erai', exc_info=True)
            erai = None
            break
        else:
            break
    erai = [series(anime) for anime in erai]
    return erai

async def anime_info_pesquisa(id):
    api = 'https://api.myanimelist.net/v2'
    client_id = 'a81a1ee7e886f2f0c54ec850594667a3'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
              'X-MAL-CLIENT-ID': client_id}
    infos = ['title', 'start_date', 'end_date', 'mean', 'status', 'genres', 'num_episodes',
             'start_season', 'broadcast', 'source', 'related_anime', 'related_manga', 'synopsis']
    async with Client(headers=header, params={'fields': ','.join(infos)}) as client:
        anime_info = await client.get(api+f'/anime/{id}')
    return anime_info.json()

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

async def selecionar_ep(anime: pd.Series) -> pd.Series:
    eps = await erai_animes.extrair_ep(anime['link'])
    anime['ep'] = [{'ep': f'Episodio {ep}', 'link': eps[ep]} for ep in eps.keys()]
    return anime

async def baixar_ep_erai(ep):
    qbit = torrent.Qbit()
    await qbit.init_sessao()
    if qbit.sessao:
        await qbit.baixar(ep)

def listar_ep(anime):
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
    pass

def gerar_frames(anime, anime_path: str):
    pass

def label_log(frame: CTkFrame, texto: str):
    label = CTkLabel(frame, text=texto, font=('Arial', 15))
    return label

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
    if not os.path.exists('cookies.json'):
        await obter_cookies()
    else:
        with open('cookies.json') as arquivo:
            cookie = json.load(arquivo)
        for a in cookie.keys():
            if 'wordpress_logged_in' in a:
                return
        await obter_cookies()

def verificar_ffmpeg():
    if not os.path.exists(r'.\ffmpeg'):
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
        link = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
        subprocess.run(['powershell', '-NoProfile', '-Command', 'curl.exe', '-L', '--progress-bar',
                        '-A', f'"{user_agent}"', '-o', 'ffmpeg.zip', f'"{link}"'])
        with zipfile.ZipFile('ffmpeg.zip') as arquivo:
            arquivo.extractall('.')
        os.remove('ffmpeg.zip')
        caminho = os.listdir('.')
        caminho = [a for a in caminho if 'ffmpeg-' in a][0]
        caminho = rf'.\{caminho}'
        os.mkdir('ffmpeg')
        for i in os.scandir(caminho+r'\bin'):
            os.replace(i.path, r'.\ffmpeg\\'+i.name)
        shutil.rmtree(caminho)
    os.environ['PATH'] = os.path.join(os.path.abspath('.'), 'ffmpeg')+os.pathsep+os.environ.get('PATH', '')

def dataset() -> pd.DataFrame:
    colunas = ['nome_pesquisa', 'info', 'caminho', 'link', 'imagem', 'id', 'ep']
    data = pd.DataFrame(columns=colunas)
    data.index.name = 'Anime'
    data.index = data.index.astype(str)
    return data

def adicionar_anime(data: pd.DataFrame, anime: pd.Series) -> pd.DataFrame:
    data.loc[anime.name] = anime
    with open('dados.parquet', 'wb') as arquivo:
        data.to_parquet(arquivo)
    return data

def criar_pasta(anime: pd.Series) -> pd.Series:
    caminho = '_'.join(anime.name.split())
    caminho = os.path.join(path, caminho)
    os.makedirs(caminho, exist_ok=True)
    anime['caminho'] = caminho
    return anime
