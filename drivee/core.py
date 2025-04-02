from fera.animes_geral import obter_escolha_valida as ob
from sakura import Sakura
from bakashi.bakashi_anime import episodios, player
import logging
from fera.animes_geral import verifica
import os

path = os.getenv('caminho')
save = os.getenv('save')

class Anime:
    def __init__(self, nome, link=None):
        self.nome_pesquisa = None
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
        self = tratar_nome(self)
        verifica(self)
        if isinstance(esco, int):
            self.ep = self.ep[esco]
            if self.ep.server == 'Mediafire':
                logging.info(f'Episodio {self.nome} escolhido para download')
                self.ep.caminho = os.path.join(path, '_'.join(self.nome.split()), self.ep.nome)
            elif self.ep.server == 'Bakashi':
                logging.info(f'Episodio numero {' '.join(self.ep.nome.split()[1:])} escolhido para download')
                self.ep.nome = '_'.join(self.nome.split())+'_'+'_'.join(self.ep.nome.split())
                self.ep.caminho = os.path.join(path, '_'.join(self.nome.split()), self.ep.nome)
            else:
                logging.info(f'Episodio numero {self.ep.nome.split()[1]} escolhido para download')
                self.ep.caminho = os.path.join(path, '_'.join(self.nome.split()))
        elif not self.ep:
            pass
        else:
            self.ep = [self.ep[int(e)] for e in esco.split('-')]
            if self.ep[0].server == 'Mediafire':
                for ep in self.ep:
                    ep.caminho = os.path.join(path, '_'.join(self.nome.split()), ep.nome)
                logging.info(f'{len(self.ep)} episodios escolhidos para download')
            elif self.ep[0].server == 'Bakashi':
                for ep in self.ep:
                    ep.nome = '_'.join(self.nome.split())+'_'+'_'.join(ep.nome.split())
                    ep.caminho = os.path.join(path, '_'.join(self.nome.split()), ep.nome)
                logging.info(f'{len(self.ep)} episodios escolhidos para download')
            else:
                for ep in self.ep:
                    ep.caminho = os.path.join(path, '_'.join(self.nome.split()))
                logging.info(f'Episodios '+', '.join([nep.nome.split()[1] for nep in self.ep])+'escolhidos para download')
        logging.info(f'Path do anime {self.nome} gerado')

class Ep:
    def __init__(self, nome, link, estensao=None, server=None):
        self.nome = nome
        self.link = link
        self.estensao = estensao
        self.server = server
        self.caminho = None

def tratar_nome(anime: Anime):
    lista_negra = [':', '°', '?', '-', ',', '“', '”', '.']
    limpo = ' '.join([''.join([letra for letra in palavra if letra not in lista_negra]) for palavra in anime.nome.split()])
    anime.nome_pesquisa = anime.nome
    anime.nome = limpo
    logging.info(f'Nome do anime {limpo} tratado')
    return anime

def escolher_animes_erai(animes: dict):
    if not animes:
        logging.warning('Nenhum anime encontrado')
        print('Nenhum anime encontrado')
        return None
    else:
        print('='*30)
        for i, anime in enumerate(animes.keys()):
            print(f'[{i}] {anime}')
        esco = ob('Escolha o anime ou digite sair: ', (0, len(animes)), True)
        if not isinstance(esco, int):
            return None
        anime = Anime(list(animes.keys())[esco], 'Erai')
        eps = animes[list(animes.keys())[esco]]
        eps = [Ep('Episódio '+eps['eps'][ep], eps['links'][ep]) for ep in range(len(eps['eps']))].__reversed__()
        anime.ep = list(eps)
        anime.listar()
        return anime
        
def escolher_anime_sakura(animes: list|Anime, baixar=False):
    if not baixar:
        if not animes:
            logging.info('Nenhum anime encontrado na Sakura')
            print('Nenhum anime entrado')
            return None
        for i, anime in enumerate(animes):
            print(f'[{i}] {anime.nome}')
        esco = ob('Escolha um anime ou digite sair: ', (0, len(animes)), True)
        if not isinstance(esco, int):
            logging.info('Nenhum anime escolhido na Sakura')
            return None
        anime = animes[esco]
    else:
        anime = animes
    anime = Sakura.listar_episodios(anime)
    anime.listar()
    if not anime.ep:
        return None
    anime.ep = Sakura.link_ep_mediafire(anime.ep)
    return anime

def escolher_anime_bakashi(animes: list|Anime, baixar=False):
    if not baixar:
        if not animes:
            logging.info('Nenhum anime encontrado no Bakashi')
            print('Nenhum anime encontrado')
            return None
        for i, anime in enumerate(animes):
            print(f'[{i}] {anime.nome}')
        esco = ob('Escolha um anime ou digite sair: ', (0, len(animes)), True)
        if not isinstance(esco, int):
            logging.info('Nenhum anime escolhido no Bakashi')
            return None
        anime = animes[esco]
    else:
        anime = animes
    anime = episodios(anime)
    if not anime:
        return None
    anime.ep = [Ep(ep['nome'], ep['link'], server='Bakashi') for ep in anime.ep]
    anime.listar()
    if not anime.ep:
        return None
    if isinstance(anime.ep, list):
        anime.ep = [player(ep) for ep in anime.ep]
        for ep in anime.ep:
            if isinstance(ep, tuple):
                logging.warning(f'Player não existe no episodio {ep[1].nome}')
                return None
            ep.caminho += ep.estensao
    else:
        anime.ep = player(anime.ep)
        if isinstance(anime.ep, tuple):
            logging.warning(f'Player não existe no episodio {anime.ep[1].nome}')
            return None
        anime.ep.caminho += anime.ep.estensao
    return anime