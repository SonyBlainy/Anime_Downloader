from httpx import AsyncClient as Client
import navegador
import zipfile
import re
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from erai import erai_animes, torrent
from erai.erai_animes import ErroCookie
from topanimes import top_animes
from infinite import infinite
from random import uniform
import logging
import os
import sys
import subprocess
import shutil
import asyncio
from customtkinter import CTkLabel, CTkFrame
import customtkinter as ctk
from PIL import Image
import pandas as pd
import io
from deep_translator import GoogleTranslator as GT

path = os.getenv('caminho')

def divisor(lista, tamanho=5):
    for i in range(0, len(lista), tamanho):
        yield lista[i:i+tamanho]

async def pesquisa_info(anime:dict) -> dict:
    tradutor = GT('en', 'pt')
    try:
        if 'id' in anime.keys():
            anime['info'] = await anime_info_pesquisa(anime['id'], info_anime=True)
        else:
            anime['info'] = await anime_info_pesquisa(nome=anime['nome'], pesquisa=True)
            anime['id'] = anime['info']['id']
    except:
        return None
    link = anime['info']['main_picture']['large']
    async with Client(timeout=40) as client:
        pagina = await client.get(link)
        imagem = pagina.content
    anime['imagem'] = imagem
    lista_negra = [':', '°', '?', '-', ',', '“', '”', '.', '\\', '/']
    limpo = ' '.join([''.join([letra for letra in palavra if letra not in lista_negra]) for palavra in anime['nome'].split()])
    anime['nome_pesquisa'] = anime['nome']
    anime['nome'] = limpo
    logging.info(f'Nome do anime {limpo} tratado')
    anime['info']['synopsis'] = tradutor.translate('.'.join(anime['info']['synopsis'].split('.')[:-1]))
    anime['info']['status'] = tradutor.translate(' '.join(anime['info']['status'].split('_')))
    anime['info']['genres'] = [tradutor.translate(g['name']) for g in anime['info']['genres']]
    try:
        anime['info']['broadcast'] = data_info(anime['info']['broadcast'])
    except:
        anime['info']['broadcast'] = {}
    else:
        anime['info']['broadcast']['dia'] = tradutor.translate(anime['info']['broadcast']['dia'])
    return anime

def series(anime:dict) -> pd.Series:
    anime = pd.Series(anime, name=anime['nome'])
    anime = anime.drop('nome')
    return anime

async def pesquisar(nome:str, reversa=False):
    while True:
        try:
            erai = await erai_animes.pesquisar(nome)
            if erai:
                lista = []
                if not reversa:
                    animes = [top_animes.pesquisar(nome), infinite.pesquisar(nome)]
                    animes = await asyncio.gather(*animes)
                    for f in animes:
                        lista.extend(f)
                    lista = [pesquisa_info(a) for a in lista]
            elif not reversa:
                animes = [top_animes.pesquisar(nome), infinite.pesquisar(nome)]
                animes = await asyncio.gather(*animes)
                lista = []
                for f in animes:
                    lista.extend(f)
                lista = [pesquisa_info(a) for a in lista]
            resultado = []
            for chunck in divisor(lista):
                c = await asyncio.gather(*chunck)
                resultado.extend([a for a in c if a])
        except ErroCookie:
            await obter_cookies()
            continue
        except:
            logging.warning('Erro ao obter animes de erai', exc_info=True)
            erai = None
            break
        else:
            break
    erai = [series(anime) for anime in resultado]
    return erai

async def anime_info_pesquisa(id=None, nome=None, info_anime=False, pesquisa=False):
    api = 'https://api.myanimelist.net/v2'
    client_id = 'a81a1ee7e886f2f0c54ec850594667a3'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
              'X-MAL-CLIENT-ID': client_id}
    infos = ['title', 'start_date', 'end_date', 'mean', 'status', 'genres', 'num_episodes',
             'start_season', 'broadcast', 'source', 'related_anime', 'related_manga', 'synopsis']
    async def info_id(id):
        async with Client(headers=header) as client:
            anime_info = await client.get(api+f'/anime/{id}', params={'fields': ','.join(infos)})
            if anime_info.status_code != 200:
                raise Exception('Erro ao obter informações, descartando anime')
        return anime_info.json()
    async def pesquisa_id(nome: str):
        async with Client(headers=header) as client:
            anime = await client.get(api+'/anime', params={'q': nome})
        return anime.json()
    if info_anime:
        anime = await info_id(id)
    elif pesquisa:
        anime = await pesquisa_id(nome)
        anime = anime['data'][0]['node']['id']
        anime = await info_id(anime)
    return anime

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
    if anime['server'] == 'Erai':
        eps = await erai_animes.extrair_ep(anime['link'])
    elif anime['server'] == 'TopAnimes':
        eps = await top_animes.episodios(anime['link'])
    elif anime['server'] == 'Infinite':
        eps = await infinite.episodios(anime['link'])
    anime['ep'] = [{'ep': f'Episodio {ep}', 'link': eps[ep]} for ep in eps.keys()]
    return anime

async def baixar_ep_erai(ep):
    qbit = torrent.Qbit()
    await qbit.init_sessao()
    if qbit.sessao:
        await qbit.baixar(ep)

async def baixar_ep_top_animes(ep, frame: CTkFrame):
    frame_barra = CTkFrame(frame, fg_color='transparent')
    frame_barra.pack(fill='both', expand=True)
    label = CTkLabel(frame_barra, text=f'Baixando {ep['ep']}... 0%', font=('Arial', 15))
    label.pack(side='left', padx=10)
    barra = ctk.CTkProgressBar(frame_barra)
    barra.pack(expand=True, fill='x', padx=10)
    barra.set(0)
    def callback(progresso: float, velocidade: float):
        barra.set(progresso)
        label.configure(text=f'Baixando {ep['ep']}... {progresso*100:.2f}%   {velocidade}')
    await top_animes.baixar(ep, callback)

async def baixar_ep_infinite(ep, frame: CTkFrame):
    frame_barra = CTkFrame(frame, fg_color='transparent')
    frame_barra.pack(fill='both', expand=True)
    label = CTkLabel(frame_barra, text=f'Baixando {ep['ep']}... 0%', font=('Arial', 15))
    label.pack(side='left', padx=10)
    barra = ctk.CTkProgressBar(frame_barra)
    barra.pack(expand=True, fill='x', padx=10)
    barra.set(0)
    def callback(progresso: float, velocidade: float):
        barra.set(progresso)
        label.configure(text=f'Baixando {ep['ep']}... {progresso*100:.2f}%   {velocidade}')
    await infinite.baixar(ep, callback)

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
    
def deletar_anime(anime: pd.Series, dados: pd.DataFrame) -> pd.DataFrame:
    shutil.rmtree(anime['caminho'])
    dados = dados.drop(anime.name)
    return dados

async def torrent_info():
    pass

def gerar_frames(anime: pd.Series) -> dict:
    eps = {}
    for ep in os.scandir(anime['caminho']):
        ep_n = re.search(r' - (\d{1,2}) ', ep.name).group(1)
        duracao = subprocess.run(['ffprobe.exe', '-v', 'quiet', '-show_entries', 'format=duration',
                                  '-of', 'csv=p=0', ep.path], capture_output=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
        duracao = float(duracao.stdout.decode().strip())
        tempo = uniform(0, duracao*0.95)
        comando = subprocess.run(['ffmpeg.exe', '-ss', str(tempo), '-i', ep.path, '-vframes', '1',
                                  '-q:v', '2', '-f', 'mjpeg', 'pipe:1'],
                                  stderr=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
        if comando.returncode == 0:
            imagem = Image.open(io.BytesIO(comando.stdout))
            eps[str(ep_n)] = imagem
    return eps

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
    colunas = ['nome_pesquisa', 'info', 'caminho', 'link', 'imagem', 'id', 'ep', 'server']
    data = pd.DataFrame(columns=colunas)
    data.index.name = 'Anime'
    data.index = data.index.astype(str)
    return data

def adicionar_anime(data: pd.DataFrame, anime: pd.Series) -> pd.DataFrame:
    data.loc[anime.name] = anime
    with open('dados.parquet', 'wb') as arquivo:
        data.to_parquet(arquivo)
    return data

def criar_pasta(anime: pd.Series, existe=False) -> pd.Series:
    caminho = '_'.join(anime.name.split())
    if not existe:
        caminho = os.path.join(path, caminho)+f'-{anime['id']}'
        os.makedirs(caminho, exist_ok=True)
    else:
        caminho = os.path.join(path, caminho)
        os.rename(caminho, caminho+f'-{anime['id']}')
    anime['caminho'] = caminho
    return anime

async def verificar_animes(animes_data: pd.DataFrame, vazio=False):
    async def info(id):
        dados = await anime_info_pesquisa(id, info_anime=True)
        nome_limpo = ' '.join([''.join([letra for letra in palavra if letra not in ['.']]) for palavra in dados['title'].split()])
        dados = await pesquisar(nome_limpo, True)
        dados = await selecionar_ep([a for a in dados if a['id'] == id][0])
        dados = criar_pasta(dados)
        return dados
    for d in os.scandir(path):
        try:
            id = int(d.name.split('-')[-1])
        except:
            nome = ' '.join(d.name.split('_'))
            try:
                dados = await pesquisar(nome)
                if not dados:
                    raise ValueError('Nenhum anime encontrado, apagando pasta...')
            except:
                shutil.rmtree(d.path)
                continue
            else:
                dados = await selecionar_ep(dados[0])
                dados = criar_pasta(dados, True)
                animes_data.loc[dados.name] = dados
                del dados
        else:
            if not vazio:
                if id not in animes_data['id'].values:
                    dados = await info(id)
                else:
                    continue
            else:
                dados = await info(id)
            if 'dados' in locals():
                animes_data.loc[dados.name] = dados
                del dados
    animes_lista = [int(a.split('-')[-1]) for a in os.listdir(path)]
    for id in animes_data['id'].to_list():
        if id not in animes_lista:
            animes_data = animes_data[animes_data['id'] != id]
    with open('dados.parquet', 'wb') as arquivo:
        animes_data.to_parquet(arquivo)
    return animes_data

def mover_arquivo(arquivo: str, destino: str):
    shutil.move(arquivo, destino)
