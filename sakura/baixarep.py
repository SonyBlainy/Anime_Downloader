import requests
import shutil
from tqdm.auto import tqdm
import os
usuario = os.getlogin()

def baixarar(link, nome, path, plata, cookie=None):
    cabeca = {'Accept-Encoding': '*', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    if plata == 'Uloz':
        with requests.get(link, stream=True, headers=cabeca, cookies=cookie) as arquivo:
            total = int(arquivo.headers.get('Content-Length'))
            with tqdm.wrapattr(arquivo.raw, 'read', total) as raw:
                with open(path+nome, 'wb') as f:
                    shutil.copyfileobj(raw, f)
    else:
        with requests.get(link, stream=True, headers=cabeca) as arquivo:
            total = int(arquivo.headers.get('Content-Length'))
            with tqdm.wrapattr(arquivo.raw, 'read', total) as raw:
                with open(path+nome, 'wb') as f:
                    shutil.copyfileobj(raw, f)
