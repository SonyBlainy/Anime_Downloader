from fera.animes_geral import obter_escolha_valida as ob
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
        if isinstance(esco, int):
            self.ep = self.ep[esco]
            logging.info(f'Episodio numero {self.ep.nome.split()[1]} escolhido para download')
            self = tratar_nome(self)
            verifica(self)
        elif not self.ep:
            pass
        else:
            self.ep = [self.ep[int(e)] for e in esco.split('-')]
            logging.info(f'Episodios '+', '.join([nep.nome.split()[1] for nep in self.ep])+'escolhidos para download')

 
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
    base_path = os.path.join(path, '_'.join(limpo.split()))
    anime.nome_pesquisa = anime.nome
    anime.nome = limpo
    logging.info(f'Nome do anime {limpo} tratado')
    anime.ep.caminho = base_path
    logging.info(f'Path do anime {limpo} gerado')
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
        