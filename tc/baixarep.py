import requests
import shutil
from tqdm.auto import tqdm

def baixarar(ep):
    cabeca = {'Accept-Encoding': '*', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    c = {'accountToken': '9EV9xTdiDoQL334CBpB60nPe8K2Rcwtc'}
    with requests.get(ep.link, stream=True, headers=cabeca, cookies=c, allow_redirects=False) as arquivo:
        total = int(arquivo.headers.get('Content-Length'))
        with tqdm.wrapattr(arquivo.raw, 'read', total) as raw:
            with open(ep.caminho+f'\\{ep.nome}', 'wb') as f:
                shutil.copyfileobj(raw, f)
