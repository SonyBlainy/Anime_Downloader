import pickle
import requests
from lxml.html import fromstring
import os

path = f"C:\\Users\\{os.getlogin()}\\Desktop\\animes\\"
save = "C:\\Users\\Micro\\AppData\\Local\\Anime_downloader\\"

def tratar(ep):
    nome = ep['nome']
    nome = nome.split()
    limpo = []
    for i, palavra in enumerate(nome):
        limpo.append(''.join([letra for letra in palavra if letra not in [':', '°', '?']]))
    limpo = ' '.join(limpo)
    ep['nome'] = limpo
    nome = ' '.join(limpo.split())
    r = requests.get(ep['ep']['ep_link'])
    html = fromstring(r.content)
    estensao = html.findtext('.//title')
    try:
        estensao = estensao.split()
    except:
        return False
    else:
        estensao = estensao[-4].split('.')[-1]
        ep['ep']['nome'] = '_'.join(ep['nome'].split())+'_'+'_'.join(ep['ep']['ep'].split())+f'.{estensao}'
        ep['ep']['caminho'] = path+'_'.join(ep['nome'].split())
        ep['ep'].pop('nome_link')
        return ep
