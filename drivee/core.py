import requests
import logging
from fera.animes_geral import verifica
from lxml.html import fromstring
import os

path = os.getenv('caminho')
save = os.getenv('save')

class Anime:
    def __init__(self, nome, link):
        self.nome = nome
        self.link = link
        self.ep = None

    def listar(self):
        print('='*30)
        for i, ep in enumerate(self.ep):
            print(f'[{i}] {ep.nome}')
        while True:
            esco = input('Escolha qual episódio deseja baixar, ou digite sair: ')
            if esco.upper() == 'SAIR':
                self.ep = None
                break
            try:
                esco = int(esco)
                if 0 <= esco < len(self.ep):
                    break
            except:
                if '-' in esco:
                    break
                else:
                    print('Erro! Tente novamente')
        if isinstance(esco, int):
            self.ep = self.ep[esco]
            self.trat()
        elif not self.ep:
            pass
        else:
            self.ep = [self.ep[int(e)] for e in esco.split('-')]

    def trat(self):
        self = tratar(self, self.ep.estensao)
        verifica(self)
        
class Ep:
    def __init__(self, nome, link, estensao, server):
        self.nome = nome
        self.link = link
        self.estensao = estensao
        self.server = server
        self.caminho = None

def tratar(anime, estensao=None):
    nome = anime.nome
    nome = nome.split()
    limpo = []
    for palavra in nome:
        limpo.append(''.join([letra for letra in palavra if letra not in [':', '°', '?', '-', ',', '“', '”', '.']]))
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
