import pickle
import os
path = os.getenv('caminho')
save = os.getenv('save')

def listar():
    for i, (caminho, diretorio, arquivo) in enumerate(os.walk(path)):
        if len(diretorio) > 0 and i == 0:
            for i, d in enumerate(diretorio):
                print(f'[{i}] {d}')
            while True:
                esc = str(input('Escolha um anime ou digite sair: '))
                try:
                    esc = int(esc)
                    esc = diretorio[esc]
                except:
                    if esc.upper() == 'SAIR':
                        break
                else:
                    break
        if esc == 'SAIR':
            break
        else:
            if os.getenv('pc') != 'Linux':
                if caminho.split('\\')[-1] == esc:
                    print('='*30)
                    for i, a in enumerate(arquivo):
                        print(f'[{i}] {a}')
                    while True:
                        esc = str(input('Escolha um episódio, digite sair ou baixar: '))
                        try:
                            esc = int(esc)
                        except:
                            if esc.upper() == 'SAIR':
                                break
                            elif esc.upper() == 'BAIXAR':
                                nome = caminho.split('\\')[-1]
                                try:
                                    with open(save+'\\'+nome+'\\'+'linkzinho.txt', 'rb') as arquivo:
                                        dados = pickle.load(arquivo)
                                except:
                                    print('Erro! Arquivo não existe, baixe um episodio do anime para criar')
                                else:
                                    if 'animefire' in dados.link:
                                        dados.site = 'Fire'
                                    elif 'sakuraanimes' in dados.link:
                                        dados.site = 'Sakura'
                                    elif 'fenixfansub' in dados.link:
                                        dados.site = 'Fenix'
                                    return dados
                        else:
                            if 0 <= esc < len(arquivo):
                                os.popen(f'{caminho}\\{arquivo[esc]}')
            else:
                if caminho.split('/')[-1] == esc:
                    print('='*30)
                    for i, a in enumerate(arquivo):
                        print(f'[{i}] {a}')
                    while True:
                        esc = str(input('Escolha um episódio, digite sair ou baixar: '))
                        try:
                            esc = int(esc)
                        except:
                            if esc.upper() == 'SAIR':
                                break
                            elif esc.upper() == 'BAIXAR':
                                nome = caminho.split('/')[-1]
                                try:
                                    with open(save+'/'+nome+'/'+'linkzinho.txt', 'rb') as arquivo:
                                        dados = pickle.load(arquivo)
                                except:
                                    print('Erro! Arquivo não existe, baixe um episodio do anime para criar')
                                else:
                                    if 'animefire' in dados.link:
                                        dados.site = 'Fire'
                                    elif 'sakuraanimes' in dados.link:
                                        dados.site = 'Sakura'
                                    elif 'animesonline' in dados.link:
                                        dados.site = 'Online'
                                    return dados
                        else:
                            if 0 <= esc < len(arquivo):
                                print(arquivo[esc])
                                print(caminho)
                                os.popen(f'vlc {caminho}/{arquivo[esc]}')


def verifica(anime) -> None:
    nome = '_'.join(anime.nome.split())
    if os.getenv('pc') == 'Linux':
        if not os.path.isdir(path+'/'+nome):
            os.mkdir(path+'/'+nome)
            os.mkdir(save+'/'+nome)
            with open(save+'/'+nome+'/'+'linkzinho.txt', 'wb') as arquivo:
                pickle.dump(anime, arquivo)
    else:
        if not os.path.isdir(path+'\\'+nome):
            os.mkdir(path+'\\'+nome)
            os.mkdir(save+'\\'+nome)
            with open(save+'\\'+nome+'\\'+'linkzinho.txt', 'wb') as arquivo:
                pickle.dump(anime, arquivo)
