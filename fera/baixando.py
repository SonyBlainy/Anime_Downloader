import requests
import shutil
from tqdm.auto import tqdm

def baixarar(anime):
    if anime.ep.server == 'Mediafire' or anime.ep.server == 'online':
        b = f'{anime.ep.nome}'
    else:
        b = f'{anime.ep.nome}.rar'
    cabeca = {'Accept-Encoding': '*', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    with requests.get(anime.ep.link, stream=True, headers=cabeca) as arquivo:
        total = int(arquivo.headers['Content-Length'])
        with tqdm.wrapattr(arquivo.raw, 'read', total) as raw:
            with open(anime.ep.caminho+f'\\{b}', 'wb') as f:
                shutil.copyfileobj(raw, f)
