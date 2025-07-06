import requests
import os
from sakura import baixarep
import zipfile
from time import sleep as mimir

def atualizar(versao):
    link = "https://api.github.com/repos/SonyBlainy/Anime_Downloader/releases/latest"
    r = requests.get(link)
    data = r.json()
    if data['tag_name'] != versao:
        link = data['assets'][0]['browser_download_url']
        resultado = {'link': link, 'path': '..\\', 'nome': 'Anime_Downloader.zip'}
        baixarep.baixarar(resultado['link'], resultado['nome'], resultado['path'])
        with zipfile.ZipFile(resultado['path']+resultado['nome']) as arquivo:
            arquivo.extractall(resultado['path'])
        os.remove(resultado['path']+resultado['nome'])
        print('Atualização concluída')
        mimir(3)
        quit()
    else:
        return None
    