import platform
import os
if platform.system() == 'Linux':
    if not os.path.isdir('/root/animes'):
        os.mkdir('/root/animes')
    if not os.path.isdir('/root/.save'):
        os.mkdir('/root/.save')
    os.environ['caminho'] = '/root/animes'
    os.environ['save'] = '/root/.save'
    os.environ['pc'] = 'Linux'
else:
    if not os.path.isdir(rf'C:\Users\{os.getlogin()}\Desktop\Animes'):
        os.mkdir(rf'C:\Users\{os.getlogin()}\Desktop\Animes')
    if not os.path.isdir(os.path.expandvars(r'%LOCALAPPDATA%\Anime_downloader')):
        os.mkdir(os.path.expandvars(r'%LOCALAPPDATA%\Anime_downloader'))
    os.environ['pc'] = 'Windows'
    os.environ['save'] = os.path.expandvars(r'%LOCALAPPDATA%\Anime_downloader')
    os.environ['caminho'] = rf'C:\Users\{os.getlogin()}\Desktop\Animes'
import logging
logging.basicConfig(filename='log.log', filemode='w', level=logging.CRITICAL)
from sakura import Sakura
from fire import fire
from fera import animes_geral

sair = False

while not sair:
    print('='*30)
    print('MENU'.center(30))
    print('='*30)
    print('[1] Pesquisar um anime')
    print('[2] Listar episódios baixados')
    print('[0] Sair')
    print('='*30)
    while True:
        try:
            esco = int(input('Escolha uma opção: '))
        except:
            print('Erro! tente novamente')
        else:
            break
    if esco == 0:
        sair = True
    elif esco == 1:
        print('='*30)
        print('[1] Animes Fire')
        print('[2] Sakura')
        print('[3] Animes Online')
        while True:
            try:
                esco = int(input('Escolha em site deseja pesquisar: '))
            except:
                print('Erro! Tente novamente')
            else:
                if esco >= 1 and esco <= 3:
                    break
                else:
                    print('Erro! Opção inválida')
        if esco == 1:
            nome = str(input('Digite o nome do anime: '))
            anime = fire.pesquisa(nome)
            print('='*30)
            if len(anime) == 0:
                print('Nenhum anime encontrado')
            else:
                for i, r in enumerate(anime):
                    print(f'[{i}] {r.nome}')
                while True:
                    escolha = str(input('Escolha um anime ou digite sair: '))
                    try:
                        escolha = int(escolha)
                    except:
                        if escolha.upper() == 'SAIR':
                            break
                        else:
                            print('Erro! Tente novamente')
                    else:
                        break
                if type(escolha) == int:
                    anime = fire.episodios(anime[escolha])
                    anime.listar()
                    if type(anime.ep) == list:
                        anime.tratar()
                        copia = anime
                        for ep in anime.ep:
                            copia.ep = ep
                            ani.baixar(copia)
                    else:
                        anime.trat()
        elif esco == 2:
            nome = str(input('Digite o nome do anime: '))
            resul = Sakura.pesquisar_anime(nome)
            if resul == []:
                print('Nenhum anime encontrado')
            else:
                print('='*30)
                for i, a in enumerate(resul):
                    print(f'[{i}] {a.nome}')
                while True:
                    esco = str(input('Escolha o anime que deseja baixar ou digite sair: '))
                    try:
                        esco = int(esco)
                    except:
                        if esco.upper() == 'SAIR':
                            break
                        else:
                            print('Erro! Tente novamente')
                    else:
                        if esco >= 0 and esco < len(resul):
                            break
                        else:
                            print('Erro! Opção inválida')
                if type(esco) == int:
                    anime = resul[esco]
                    anime.eps()
                    anime.listar()
                    if type(anime.ep) == list:
                        copia = anime
                        for ep in anime.ep:
                            copia.ep = ep
                            copia.trat()
                            Sakura.mediafire(copia)
                    else:
                        Sakura.mediafire(anime)
        elif esco == 3:
            nome = str(input('Digite o nome do anime: '))
            animes = TC.pesquisar(nome)
            if len(animes) == 0:
                print('Nenhum anime encontrado')
            else:
                print('='*30)
                for i, a in enumerate(animes):
                    print(f'[{i}] {a.nome}')
                while True:
                    try:
                        esco = str(input('Escolha o anime que deseja baixar ou digite sair: '))
                        esco = int(esco)
                    except:
                        if esco.upper() == 'SAIR':
                            break
                        else:
                            print('Erro! Tente novamente')
                    else:
                        break
                if type(esco) == int:
                    animes = animes[esco]
                    animes.eps()
                    animes.listar()
                    if type(animes.ep) == list:
                        copia = animes
                        for ep in animes.ep:
                            copia.ep = TC.baixar(ep, varios=True)
                            copia.baixarep()
                    else:
                        animes.ep = TC.baixar(animes.ep)
                        animes.baixarep()
    elif esco == 2:
        r = animes_geral.listar()
        if r != None:
            if r.site == 'TC':
                r.eps()
                r.listar()
                if type(r.ep) == list:
                    copia = r
                    for ep in r.ep:
                        copia.ep = TC.baixar(ep, varios=True)
                        copia.baixarep()
                else:
                    r.ep = TC.baixar(r.ep)
                    r.baixarep()
            elif r.site == 'Fenix':
                anime = ani.eps(r)
                anime.listar()
                if type(anime.ep) == list:
                    anime.tratar()
                    copia = anime
                    for ep in anime.ep:
                        copia.ep = ep
                        ani.baixar(copia)
                else:
                    anime.tratar()
                    ani.baixar(anime)
            elif r.site == 'Sakura':
                anime = r
                anime.eps()
                anime.listar()
                if type(anime.ep) == list:
                    copia = anime
                    for ep in anime.ep:
                        copia.ep = ep
                        copia.trat()
                        Sakura.mediafire(copia)
                else:
                    Sakura.mediafire(anime)
