import requests
from concurrent.futures import ThreadPoolExecutor
import threading
from tqdm import tqdm

lock = threading.Lock()

def baixar_episodio(ep, posi):
    cabeca = {'Accept-Encoding': '*', 
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    with requests.get(ep.link, stream=True, headers=cabeca) as arquivo:
        total = int(arquivo.headers['Content-Length'])
        with lock:
            progresso = tqdm(total=total, desc=ep.nome, position=posi, leave=True, unit='B', unit_scale=True)
        with arquivo.raw as raw:
            raw.decode_content = True
            with open(ep.caminho, 'wb') as f:
                for chunk in iter(lambda: raw.read(4096), b""):
                    f.write(chunk)
                    progresso.update(len(chunk))
        progresso.close()
    
def download_padrao(anime):
    threads = []
    if isinstance(anime.ep, list):
        with ThreadPoolExecutor() as executor:
            executor.map(lambda ep: baixar_episodio(ep, anime.ep.index(ep)), anime.ep)
    else:
        baixar_episodio(anime.ep, 0)
    for t in threads:
        t.join()
