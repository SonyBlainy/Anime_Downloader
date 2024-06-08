import requests
from lxml.html import fromstring
import os

path = os.getenv('caminho')
save = os.getenv('save')

def tratar(anime, estensao=None):
    nome = anime.nome
    nome = nome.split()
    limpo = []
    for palavra in nome:
        limpo.append(''.join([letra for letra in palavra if letra not in [':', '°', '?', '-']]))
    limpo = ' '.join(limpo)
    anime.nome = limpo
    servers = ['Mediafire', 'Fire', 'Bakashi']
    if anime.ep.server in servers:
        anime.ep.nome = '_'.join(anime.nome.split())+'_'+'_'.join(anime.ep.nome.split())+estensao
        if os.getenv('pc') == 'Linux':
            anime.ep.caminho = path+'/'+'_'.join(anime.nome.split())+'/'
        else:
            anime.ep.caminho = path+'\\'+'_'.join(anime.nome.split())+'\\'
        anime.ep.erro = False
        return anime
    else:
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
