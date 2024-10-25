import os
import requests

save = os.getenv('save')
path = os.getenv('caminho')
api_url = 'http://127.0.0.1:8080/api/v2/'

def login() -> requests.Session:
    sessao = requests.Session()
    para = {'username': 'admin', 'password': 'admin123'}
    header = {'Referer': 'http://127.0.0.1:8080'}
    l = sessao.post(api_url+'auth/login', data=para, headers=header)
    if l.status_code != 200:
        print('Erro ao fazer Login')
        return None
    else:
        return sessao

def baixar(anime, qbit: requests.Session):
    down = qbit.post(api_url+'torrents/add', {'urls': anime.ep.link})