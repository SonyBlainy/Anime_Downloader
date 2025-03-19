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
            logging.info(f'Episodio numero {self.ep.nome.split()[1]} escolhido para download')
            self.trat()
        elif not self.ep:
            pass
        else:
            self.ep = [self.ep[int(e)] for e in esco.split('-')]
            logging.info(f'Episodios '+', '.join([nep.nome.split()[1] for nep in self.ep])+'escolhidos para download')

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

def tratar_nome(anime):
    lista_negra = [':', '°', '?', '-', ',', '“', '”', '.']
    limpo = ' '.join([''.join([letra for letra in palavra if letra not in lista_negra]) for palavra in anime.nome.split()])
    base_path = os.path.join(path, '_'.join(limpo.split()))
    anime.nome = limpo
    logging.info(f'Nome do anime {limpo} tratado')
    anime.ep.caminho = base_path
    logging.info(f'Path do anime {limpo} gerado')
    return anime

def tratar(anime, estensao=None):
    anime = tratar_nome(anime)
    servers = ['Mediafire', 'Bakashi']
    if anime.ep.server in servers:
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
