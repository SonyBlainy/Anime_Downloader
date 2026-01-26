import requests
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
import logging
import pickle
import os
import sys
import subprocess
import shutil

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

def pesquisar_tudo(nome:str):
    try:
        erai = erai_animes.pesquisar(nome)
    except:
        erai = None
    sakura = None
    q1n = None
    dados = {'Erai': erai, 'Sakura': sakura, 'Q1n': q1n}
    for chave in dados.keys():
        if dados[chave]:
            dados[chave] = [Anime(anime['nome'], anime['link'], anime['imagem']) for anime in dados[chave]]
    return dados

def anime_info_pesquisa(anime):
    api = 'https://api.myanimelist.net/v2'
    client_id = 'a81a1ee7e886f2f0c54ec850594667a3'
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'}
    header_mal = {'X-MAL-CLIENT-ID': client_id}
    infos = ['title', 'start_date', 'end_date', 'mean', 'status', 'genres', 'num_episodes',
             'start_season', 'broadcast', 'source', 'related_anime', 'related_manga', 'synopsis']
    if 'erai-raws' in anime.link:
        pagina = fromstring(requests.get(anime.link, cookies=json.load(open('cookies.json')), headers=header).content)
        anime_id = pagina.find_class('entry-content')[0].find_class('entry-content-buttons')[-2]
        anime_id = anime_id.findall('a')[-1].get('href')
        anime_id = re.findall(r'anime/(.*)', anime_id)[0]
    anime_info = requests.get(api+f'/anime/{anime_id}', params={'fields': ','.join(infos)}, headers=header_mal)
    anime.info = anime_info.json()
    return anime
    
def escolher_ep_erai(anime: Anime):
    eps = erai_animes.extrair_ep(anime.link)
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

def selecionar_ep(anime: Anime):
    eps = {'erai-raws': lambda a: escolher_ep_erai(a)}
    anime.ep = eps[re.findall(r'\.(.*)\.', anime.link)[0]](anime)
    return anime

def baixar_ep_erai(ep: Ep):
    qbit = torrent.Qbit()
    if qbit.sessao:
        qbit.baixar(ep)

def anime_info(anime_caminho):
    with os.scandir(anime_caminho) as arquivos:
        for a in arquivos:
            arquivo = a.path
            break
    return pickle.load(open(arquivo, 'rb'))

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

def update(versao):
    link = 'https://api.github.com/repos/SonyBlainy/Anime_Downloader/releases/latest'
    r = requests.get(link)
    data = r.json()
    if data['tag_name'] != versao:
        link = data['assets'][0]['browser_download_url']
        caminho = os.path.expandvars(r'%temp%\anime_downloader_temp')
        os.makedirs(caminho, exist_ok=True)
        caminho = os.path.join(caminho, 'instalador.exe')
        subprocess.run(['powershell', '-NoProfile', '-Command', 'wget', link, '-O', caminho],
                    encoding='utf-8')
        os.startfile(caminho)
        sys.exit()
