import requests
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
from tqdm import tqdm
import os

cabeca = {'Accept-Encoding': '*', 
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
lock = threading.Lock()

def arquivo_ts(ep):
    os.mkdir('temp_ts')
    contador = 1
    for i, n in enumerate(ep.link.copy()):
        ep.link[i] = (n, f'segmento{contador}')
        contador += 1
    with ThreadPoolExecutor() as executor:
        executor.map(lambda ep: baixar_ts(ep[0], ep[1]), ep.link)
    print('Concatenando arquivos...')
    lista_arquivos = os.listdir('temp_ts')
    lista_arquivos.sort()
    with open('temp_ts\\segmentos.txt', 'w') as segmento:
        for arquivo in lista_arquivos:
            segmento.write(f'file {arquivo}\n')
    os.system(f'cd temp_ts && ffmpeg -f concat -safe 0 -i segmentos.txt -c:v libx264 -c:a aac {ep.caminho}')

def baixar_ts(link, nome, caminho='temp_ts'):
    with requests.get(link, stream=True, headers=cabeca) as arquivo:
        with arquivo.raw as raw:
            raw.decode_content = True
            with open(f'{caminho}\\{nome}.ts', 'wb') as f:
                for chunk in arquivo.iter_content(chunk_size=4096):
                    f.write(chunk)

def baixar_episodio(ep, posi):
    if isinstance(ep.link, list):
        print(f'Baixando os {len(ep.link)} segmentos do arquivo de vídeo...')
        arquivo_ts(ep)
        return None
    try:
        logging.info('Iniciando download padrão')
        with requests.get(ep.link, stream=True, headers=cabeca) as arquivo:
            total = int(arquivo.headers['Content-Length'])
            with lock:
                progresso = tqdm(total=total, desc=ep.nome, position=posi, leave=True, unit='B', unit_scale=True)
            with arquivo.raw as raw:
                raw.decode_content = True
                with open(ep.caminho, 'wb') as f:
                    for chunk in arquivo.iter_content(chunk_size=4096):
                        f.write(chunk)
                        progresso.update(len(chunk))
            progresso.close()
        logging.info('Donwload concluido')
    except requests.RequestException as e:
        logging.error(f'Erro ao baixar {ep.nome}: {e}')
    
def download_padrao(anime):
    if isinstance(anime.ep, list):
        logging.info(f'Iniciando o download paralelo de {len(anime.ep)} episodios')
        with ThreadPoolExecutor() as executor:
            executor.map(lambda ep: baixar_episodio(ep, anime.ep.index(ep)), anime.ep)
        logging.info('Downloads encerrados')
    else:
        logging.info(f'Iniciando download de {anime.ep.nome}')
        baixar_episodio(anime.ep, 0)
