from fera.animes_geral import obter_escolha_valida as ob
from infinite import infinete
from fera import baixando
from sakura import Sakura
from erai import nyaa
from bakashi import bakashi_anime
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

def escolher_animes_erai(nome:str):
    animes = nyaa.pesquisar(nome)
    if not animes:
        logging.warning('Nenhum anime encontrado')
        print('Nenhum anime encontrado')
        return None
    else:
        anime = Anime(animes['nome'], 'Erai')
        eps = list(animes['eps'].keys())
        eps = [Ep('Episódio '+eps[i], animes['eps'][ep]) for i, ep in enumerate(eps)].__reversed__()
        anime.ep = list(eps)
        anime.listar()
        nyaa.baixar_anime(anime)
        
def escolher_anime_sakura(nome=None, animes=None, baixar=False):
    if not baixar:
        animes = Sakura.pesquisar_anime(nome)
        animes = [Anime(anime['nome'], anime['link']) for anime in animes]
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
    anime.ep = [Ep(ep['nome'], ep['link'], server='Mediafire', estensao='.mp4') for ep in anime.ep]
    anime.listar()
    if not anime.ep:
        return None
    if 'sakuraanimes' in anime.ep.link:
        if isinstance(anime.ep, list):
            anime.ep = [Sakura.sakura_link(ep) for ep in anime.ep]
        else:
            anime.ep = Sakura.sakura_link(anime.ep)
    anime.ep = Sakura.link_ep_mediafire(anime.ep)
    anime.ep.caminho = os.path.join(os.path.split(anime.ep.caminho)[0], anime.ep.nome)
    baixando.download_padrao(anime)

def escolher_anime_bakashi(nome=None, animes=None, baixar=False):
    if not baixar:
        animes = bakashi_anime.pesquisar(nome)
        animes = [Anime(anime['nome'], anime['link']) for anime in animes]
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
    anime = bakashi_anime.episodios(anime)
    if not anime:
        return None
    anime.ep = [Ep(ep['nome'], ep['link'], server='Bakashi', estensao=ep['estensao']) for ep in anime.ep]
    anime.listar()
    if not anime.ep:
        return None
    if isinstance(anime.ep, list):
        for ep in anime.ep:
            ep.caminho += ep.estensao
    else:
        anime.ep.caminho += anime.ep.estensao
    baixando.download_padrao(anime)

def escolher_animes_infinite(nome=None, animes=None, baixar=False):
    if not baixar:
        animes = infinete.pesquisar(nome)
        animes = [Anime(anime['nome'], anime['link']) for anime in animes]
        if not animes:
            logging.info('Nenhum anime encontrado no Infinite')
            print('Nenhum anime encontrado')
            return None
        for i, anime in enumerate(animes):
            print(f'[{i}] {anime.nome}')
        esco = ob('Escolha um anime ou digite sair: ', (0, len(animes)), True)
        if not isinstance(esco, int):
            logging.info('Nenhum anime escolhido no Infinite')
            return None
        anime = animes[esco]
    else:
        anime = animes
    anime = infinete.episodios(anime)
    anime.ep = [Ep(ep['nome'], ep['link'], server='Mediafire', estensao='.mp4') for ep in anime.ep]
    anime.listar()
    if isinstance(anime.ep, list):
        for ep in anime.ep:
            ep.caminho += ep.estensao
    else:
        anime.ep.caminho += anime.ep.estensao
    if not anime.ep:
        return None
    baixando.download_padrao(anime)
    