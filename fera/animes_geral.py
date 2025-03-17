import pickle
import os
path = os.getenv('caminho')
save = os.getenv('save')

def listar():
    with os.scandir(path) as entrada:
        listar_animes = True
        lista = [a for a in entrada]
        while listar_animes:
            print('='*30)
            for indice, e in enumerate(lista):
                print(f'[{indice}] {e.name}')
            n = obter_escolha_valida('Escolha um anime ou digite sair: ', (0, len(lista)), True)
            if type(n) == int:
                with os.scandir(path) as ent2:
                    print('='*30)
                    for i, e in enumerate(ent2):
                        if i == n:
                            with os.scandir(e.path) as eps:
                                for indice, ee in enumerate(eps):
                                    print(f'[{indice}] {ee.name}')
                                while True:
                                    numero = str(input('Digite o numero do episódio, digite sair ou baixar: '))
                                    try:
                                        numero = int(numero)
                                    except:
                                        if numero.upper() == 'SAIR':
                                            break
                                        elif numero.upper() == 'BAIXAR':
                                            anime_nome = e.path.split('\\')[-1]
                                            try:
                                                with open(os.path.join(save, anime_nome, 'save.txt'), 'rb') as arquivo:
                                                    dados = pickle.load(arquivo)
                                            except:
                                                print('Arquivo não existe, baixe um episódio do anime para crialo')
                                            else:
                                                linkzinho = dados.link
                                                if linkzinho == 'sim':
                                                    dados.site = 'Erai_'+dados.nome
                                                if 'bakashi' in linkzinho:
                                                    dados.site = 'Bakashi'
                                                elif 'sakuraanimes' in linkzinho:
                                                    dados.site = 'Sakura'
                                                return dados
                                        else:
                                            print('Erro! Tente novamente')
                                    else:
                                        for ii, ep in enumerate(os.scandir(e.path)):
                                            if ii == numero:
                                                os.startfile(ep.path)
            else:
                listar_animes = False
                                
def verifica(anime) -> None:
    nome = '_'.join(anime.nome.split())
    anime_path = os.path.join(path, nome)
    save_path = os.path.join(save, nome)
    for d in (anime_path, save_path):
        os.makedirs(d, exist_ok=True)
    save_file = os.path.join(save_path, 'save.txt')
    if not os.path.isfile(save_file):
        with open(save_file, 'wb') as arquivo:
            pickle.dump(anime, arquivo)

def obter_escolha_valida(prompt, intervalo=None, sair_opcional=False):
    while True:
        escolha = input(prompt)
        if sair_opcional and escolha.upper() == 'SAIR':
            return False
        try:
            escolha = int(escolha)
            if intervalo and escolha not in range(intervalo[0], intervalo[1]+1):
                print('Erro! Opção inválida')
                continue
            return escolha
        except:
            print('Erro! Tente novamente')