import requests
import shutil
from tqdm.auto import tqdm

def download_padrao(anime):
    cabeca = {'Accept-Encoding': '*', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    if isinstance(anime.ep, list):
        for ep in anime.ep:
            with requests.get(ep.link, stream=True, headers=cabeca) as arquivo:
                total = int(arquivo.headers['Content-Length'])
                with tqdm.wrapattr(arquivo.raw, 'read', total) as raw:
                    with open(ep.caminho, 'wb') as f:
                        shutil.copyfileobj(raw, f)
    else:
        with requests.get(anime.ep.link, stream=True, headers=cabeca) as arquivo:
            total = int(arquivo.headers['Content-Length'])
            with tqdm.wrapattr(arquivo.raw, 'read', total) as raw:
                with open(anime.ep.caminho, 'wb') as f:
                    shutil.copyfileobj(raw, f)
