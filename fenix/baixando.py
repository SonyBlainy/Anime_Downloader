import requests
import shutil
from tqdm.auto import tqdm

def baixarar(anime):
    cabeca = {'Accept-Encoding': '*', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    with requests.get(anime.ep.link, stream=True, headers=cabeca) as arquivo:
        total = int(arquivo.headers['Content-Length'])
        with tqdm.wrapattr(arquivo.raw, 'read', total) as raw:
            with open(anime.ep.caminho+f'\\{anime.ep.nome}.rar', 'wb') as f:
                shutil.copyfileobj(raw, f)