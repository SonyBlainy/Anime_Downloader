import pickle
import logging
import os
path = os.getenv('caminho')
save = os.getenv('save')

def listar_animes():
    try:
        with os.scandir(path) as i:
            diretorios = [a for a in i if a.is_dir()]
            if not diretorios:
                logging.warning('Nenhum anime encontrado')
                print('Nenhum anime encontrado, baixe para adicionar')
                return None
            return diretorios
    except OSError as e:
        logging.error(f'Erro ao acessar o diretorio dos animes: {e}')

def listar_episodios(anime_nome, anime_path):
    try:
        with os.scandir(anime_path) as eps:
            episodios = list(eps)
            if not episodios:
                logging.warning(f'Nenhum episodio encontrado do anime {anime_nome}')
                print('Nenhum episodio encontrado, baixe para adicionar')
                return None
            for i, ep in enumerate(episodios):
                print(f'[{i}] {ep.name}')
            print('='*30)
            while True:
                esco = input('Escolha um episódio, digite baixar ou sair: ')
                if esco.upper() == 'SAIR':
                    return None
                elif esco.upper() == 'BAIXAR':
                    save_file = os.path.join(save, anime_nome, 'save.txt')
                    try:
                        with open(save_file, 'rb') as arquivo:
                            dados = pickle.load(arquivo)
                        link = dados.link
                        if link == 'Erai':
                            dados.site = 'Erai_'+dados.nome.pesquisa
                        elif 'bakashi' in link:
                            dados.site = 'Bakashi'
                        elif 'sakuraanimes' in link:
                            dados.site = 'Sakura'
                        return dados
                    except FileNotFoundError:
                        logging.warning(f'Save não encontrado para o anime {anime_nome}')
                        print('Save não encontrado')
                    except pickle.UnpicklingError as e:
                        logging.error(f'Save do anime {anime_nome} corrompido')
                        print('Save corrompido')
                else:
                    try:
                        esco = int(esco)
                    except:
                        logging.warning('Erro! opção invalida')
                        print('Opção inválida, tente novamente')
                    else:
                        if 0 <= esco < len(episodios):
                            logging.info(f'Abrindo episodio {episodios[esco].name} do anime {anime_nome}')
                            os.startfile(episodios[esco].path)
                        else:
                            logging.warning(f'Episodio com indice {esco} não existe')
                            print('Episódio não existe, tente novamente')
    except OSError as e:
        logging.error(f'Erro ao acessar os episodios do anime {anime_nome}')

def listar():
    animes = listar_animes()
    logging.info('Lista de animes obtida')
    while True:
        print('='*30)
        for i, anime in enumerate(animes):
            print(f'[{i}] {anime.name}')
        print('='*30)
        n = obter_escolha_valida('Escolha um anime ou digite sair: ', (0, len(animes)), True)
        if isinstance(n, int):
            logging.info(f'Listando episodios do anime {animes[n].name}')
            resultado = listar_episodios(animes[n].name, animes[n].path)
            if resultado != None:
                return resultado
        else:
            return None
                                
def verifica(anime) -> None:
    nome = '_'.join(anime.nome.split())
    anime_path = os.path.join(path, nome)
    save_path = os.path.join(save, nome)
    for d in (anime_path, save_path):
        os.makedirs(d, exist_ok=True)
    save_file = os.path.join(save_path, 'save.txt')
    if not os.path.isfile(save_file):
        try:
            with open(save_file, 'wb') as arquivo:
                pickle.dump(anime, arquivo)
            logging.info(f'Arquivo save criado para o anime {nome}')
        except OSError as e:
            logging.error(f'Erro ao criar save para o anime {nome}: {e}')

def obter_escolha_valida(prompt, intervalo=None, sair_opcional=False):
    while True:
        escolha = input(prompt)
        if sair_opcional and escolha.upper() == 'SAIR':
            return None
        try:
            escolha = int(escolha)
            if intervalo and escolha not in range(intervalo[0], intervalo[1]+1):
                print('Erro! Opção inválida')
                continue
            return escolha
        except:
            print('Erro! Tente novamente')