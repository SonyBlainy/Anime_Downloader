import platform
import os
if platform.system() == 'Linux':
    if not os.path.isdir('/home/sony/animes'):
        os.mkdir('/home/sony/animes')
    if not os.path.isdir('/home/sony/.save'):
        os.mkdir('/home/sony/.save')
    os.environ['caminho'] = '/home/sony/animes'
    os.environ['save'] = '/home/sony/.save'
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
logging.basicConfig(filename='log.log', filemode='w', level=logging.DEBUG)
from sakura import Sakura
from fera import animes_geral
from fera import baixando
from bakashi import bakashi_anime
from erai import nyaa
from erai import torrent

sair = False

while not sair:
    print('='*30)
    print('MENU'.center(30))
    print('='*30)
    print('[1] Pesquisar um anime')
    print('[2] Listar episódios baixados')
    print('[3] Qbit')
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
        print('[1] Sakura')
        print('[2] Bakashi')
        print('[3] Erai')
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
                    if anime.ep == None:
                        print('Erro ao tentar obter o link para download ou pasta de download')
                    else:
                        anime.listar()
                        if type(anime.ep) == list:
                            copia = anime
                            for ep in anime.ep:
                                copia.ep = ep
                                copia.trat()
                                try:
                                    Sakura.mediafire(copia)
                                except KeyboardInterrupt:
                                    print('Download encerrado pelo usuario')
                        else:
                            try:
                                Sakura.mediafire(anime)
                            except KeyboardInterrupt:
                                print('Download encerrado pelo usuario')
        elif esco == 2:
            nome = str(input('Digite o nome do anime: '))
            animes = bakashi_anime.pesquisar(nome)
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
                    anime = animes[esco]
                    anime = bakashi_anime.episodios(anime)
                    anime.listar()
                    if type(anime.ep) == list:
                        copia = anime
                        for ep in anime.ep:
                            copia.ep = ep
                            copia.trat()
                            try:
                                baixando.baixarar(anime)
                            except KeyboardInterrupt:
                                print('Download encerrado pelo usuario')
                    else:
                        try:
                            baixando.baixarar(anime)
                        except KeyboardInterrupt:
                            print('Download encerrado pelo usuario')
        elif esco == 3:
            nome = str(input('Digite o nome do anime: '))
            animes = nyaa.pesquisar(nome)
            if len(animes) == 0:
                print('Nenhum anime encontrado')
            else:
                print('='*30)
                for n, anime in enumerate(animes.keys()):
                    print(f'[{n}] {anime}')
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
                    eps = animes[list(animes.keys())[esco]]
                    anime = Sakura.Anime(list(animes.keys())[esco], 'sim')
                    eps = [Sakura.Ep('Episódio '+eps['eps'][e], eps['links'][e], eps['extensao'][e], 'Bakashi') for e in range(len(eps['eps'])-1, -1, -1)]
                    anime.ep = eps
                    anime.listar()
                    if type(anime.ep) == list:
                        copia = anime
                        qbit = torrent.login()
                        for ep in anime.ep:
                            copia.ep = ep
                            copia.trat()
                            torrent.baixar(copia, qbit)
                    else:
                        qbit = torrent.login()
                        torrent.baixar(anime, qbit)
    elif esco == 2:
        r = animes_geral.listar()
        if r != None:
            if r.site == 'Bakashi':
                anime = bakashi_anime.episodios(r)
                anime.listar()
                if type(anime.ep) == list:
                    copia = anime
                    for ep in anime.ep:
                        copia.ep = ep
                        copia.trat()
                        try:
                            baixando.baixarar(anime)
                        except KeyboardInterrupt:
                            print('Download encerrado pelo usuario')
                else:
                    try:
                        baixando.baixarar(anime)
                    except KeyboardInterrupt:
                        print('Download encerrado pelo usuario')
            elif r.site == 'Sakura':
                anime = r
                anime.eps()
                if anime.ep == None:
                    print('Erro ao tentar obter o link para download')
                else:
                    anime.listar()
                    if type(anime.ep) == list:
                        copia = anime
                        for ep in anime.ep:
                            copia.ep = ep
                            copia.trat()
                            try:
                                Sakura.mediafire(copia)
                            except KeyboardInterrupt:
                                print('Download encerrado pelo usuario')
                    else:
                        try:
                            Sakura.mediafire(anime)
                        except KeyboardInterrupt:
                            print('Download encerrado pelo usuario')
    elif esco == 3:
        qbit = torrent.login()
        r = torrent.infos(qbit)
        if r == []:
            print('Nenhum torrent encotrado')
        else:
            for i, t in enumerate(r):
                print(f'[{i}] {t['name']}')
            print('='*30)
            esco = 'sim'
            while True:
                try:
                    esco = int(input('Escolha um torrent para gerenciar: '))
                except KeyboardInterrupt:
                    break
                except:
                    print('Erro! Tente novamente')
                else:
                    break
            if esco != 'sim':
                print('='*30)
                r = r[esco]
                print(f'Nome: {r['name']}')
                print(f'Velocidade: {r['dlspeed']/(3*1024):.2f}Mb/s')
                print(f'Progresso: {r['progress']*100:.2f}%')
                print(f'Estado: {r['state']}')
                print('='*30)
                print('[0] Sair')
                print('[1] Pausar e deletar')
                while True:
                    try:
                        esco = int(input('Escolha o que deseja fazer: '))
                    except:
                        print('Erro! Tente novamente')
                    else:
                        break
                if esco == 1:
                    torrent.parar(qbit, r['hash'])
