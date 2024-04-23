import requests
from lxml.html import fromstring
import os

path = f"C:\\Users\\{os.getlogin()}\\Desktop\\animes\\"
save = "C:\\Users\\Micro\\AppData\\Local\\Anime_downloader\\"

def tratar(anime):
    nome = anime.nome
    nome = nome.split()
    limpo = []
    for palavra in nome:
        limpo.append(''.join([letra for letra in palavra if letra not in [':', '°', '?']]))
    limpo = ' '.join(limpo)
    anime.nome = limpo
    nome = ' '.join(limpo.split())
    r = requests.get(anime.ep.link)
    html = fromstring(r.content)
    estensao = html.findtext('.//title')
    try:
        estensao = estensao.split()
        estensao = estensao[-4].split('.')[-1]
    except:
        anime.ep.erro = True
        return anime
    else:
        anime.ep.nome = '_'.join(anime.nome.split())+'_'+'_'.join(anime.ep.nome.split())+f'.{estensao}'
        anime.ep.caminho = path+'_'.join(anime.nome.split())
        anime.ep.erro = False
        return anime
