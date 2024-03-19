import requests
import shutil
from tqdm.auto import tqdm
import os
usuario = os.getlogin()

def baixarar(link, nome, path):
    with requests.get(link, stream=True) as arquivo:
        total = arquivo.headers.get('Content-Lenght')
        with tqdm.wrapattr(arquivo.raw, 'read', total) as raw:
            with open(path+f'{nome}.rar', 'wb') as f:
                shutil.copyfileobj(raw, f)