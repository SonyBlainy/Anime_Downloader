import os
import requests

save = os.getenv('save')
path = os.getenv('caminho')
api_url = 'http://127.0.0.1:8080/api/v2/'

def login() -> requests.Session:
    if 'qbittorrent.exe' not in os.popen('tasklist').read().lower():
        os.system('powershell -Command \"qbittorrent.exe\"')
    sessao = requests.Session()
    para = {'username': 'admin', 'password': 'admin123'}
    header = {'Referer': 'http://127.0.0.1:8080'}
    l = sessao.post(api_url+'auth/login', data=para, headers=header)
    if l.status_code != 200:
        return None
    else:
        return sessao

def baixar(anime, qbit: requests.Session):
    qbit.post(api_url+'torrents/add', {'urls': anime.ep.link, 'savepath': anime.ep.caminho})

def infos(qbit: requests.Session):
    resposta = qbit.get(api_url+'torrents/info')
    return resposta.json()

def parar(qbit: requests.Session, hash: str):
    qbit.post(api_url+'torrents/stop', data={'hashes': hash})
    qbit.post(api_url+'torrents/delete', data={'hashes': hash, 'deleteFiles': 'false'})