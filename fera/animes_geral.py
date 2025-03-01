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
            while True:
                n = str(input('Escolha um anime ou digite sair: '))
                try:
                    n = int(n)
                except:
                    if n.upper() == 'SAIR':
                        break
                    else:
                        print('Erro! Tente novamente')
                else:
                    if n >= 0 and n < len(lista):
                        break
                    else:
                        print('Erro! Opção de anime incorreta')
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
                                                with open(save+'\\'+anime_nome+'\\save.txt', 'rb') as arquivo:
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
                                                os.system(f"powershell.exe -Command \"start '{ep.path}'\"")
            else:
                listar_animes = False
                                
def verifica(anime) -> None:
    nome = '_'.join(anime.nome.split())
    if os.getenv('pc') == 'Linux':
        if not os.path.isdir(path+'/'+nome):
            os.mkdir(path+'/'+nome)
        if not os.path.isdir(save+'/'+nome):
            os.mkdir(save+'/'+nome)
            with open(save+'/'+nome+'/'+'save.txt', 'wb') as arquivo:
                pickle.dump(anime, arquivo)
    else:
        if not os.path.isdir(path+'\\'+nome):
            os.mkdir(path+'\\'+nome)
        if not os.path.isdir(save+'\\'+nome):
            os.mkdir(save+'\\'+nome)
            with open(save+'\\'+nome+'\\'+'save.txt', 'wb') as arquivo:
                pickle.dump(anime, arquivo)
