import os
def configurar_diretorios():
    caminhos = {'animes': os.path.join('C:\Users', os.getlogin(), 'Desktop', 'Animes'),
                'save': os.path.expandvars(r'%LOCALAPPDATA%\Anime_downloader')}
    for pasta in caminhos.values():
        if not os.path.isdir(pasta):
            os.mkdir(pasta)
    os.environ.update({'caminho': caminhos['animes'], 'save': caminhos['save']})
configurar_diretorios()
import logging
from fera.animes_geral import obter_escolha_valida as ob
logging.basicConfig(filename='log.log', filemode='w', level=logging.DEBUG)
from sakura import Sakura
from fera import animes_geral
from fera import baixando
from bakashi import bakashi_anime
from erai import nyaa
from erai import torrent
sair = False

def menu():
    print('='*30, 'MENU'.center(30), '='*30, '[1] Pesquisar um anime', '[2] Listar episódios baixados',
          '[3] Qbit', '[0] Sair', sep='\n')

while not sair:
    texto = 'Digite o anime que deseja baixar ou digite sair: '
    menu()
    esco = ob('Escolha um opção: ', (0,3))
    if esco == 0:
        sair = True
    elif esco == 1:
        print('='*30, '[1] Sakura', '[2] Bakashi', '[3] Erai', sep='\n')
        esco = ob('Escolha em qual site deseja pesquisar: ', (1, 3), True)
        if not esco:
            continue
        if esco == 1:
            nome = str(input('Digite o nome do anime: '))
            resul = Sakura.pesquisar_anime(nome)
            if resul == []:
                print('Nenhum anime encontrado')
            else:
                print('='*30)
                for i, a in enumerate(resul):
                    print(f'[{i}] {a.nome}')
                esco = ob(texto, (0, len(resul)), True)
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
                esco = ob(texto, (0, len(animes)), True)
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
                esco = ob(texto, (0, len(animes)), True)
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
            elif r.site.split('_')[0] == 'Erai':
                nome = r.site.split('_')[1].strip()
                animes = nyaa.pesquisar(nome)
                if len(animes) == 0:
                    print('Nenhum anime encontrado')
                else:
                    print('='*30)
                    for n, anime in enumerate(animes.keys()):
                        print(f'[{n}] {anime}')
                    esco = ob(texto, (0, len(animes)), True)
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
    elif esco == 3:
        qbit = torrent.login()
        if qbit == None:
            print('Erro ao fazer login')
        else:
            r = torrent.infos(qbit)
            if r == []:
                print('Nenhum torrent encotrado')
            else:
                for i, t in enumerate(r):
                    print(f'[{i}] {t['name']}')
                print('='*30)
                while True:
                    esco = str(input('Escolha um torrent para gerenciar, ou digite 00 para deletar todos os torrents: '))
                    if esco == '00':
                        break
                    else:
                        try:
                            esco = int(esco)
                        except KeyboardInterrupt:
                            break
                        except:
                            print('Erro! Tente novamente')
                        else:
                            break
                if esco == '00':
                    for t in r:
                        torrent.parar(qbit, t['hash'])
                else:
                    print('='*30)
                    r = r[esco]
                    print(f'Nome: {r['name']}', f'Velocidade: {r['dlspeed']/(1024**2):.2f}MB/s',
                          f'Progresso: {r['progress']*100:.2f}%', f'Estado: {r['state']}', sep='\n')
                    print('='*30, '[0] Sair', '[1] Pausar e deletar', sep='\n')
                    esco = ob('Escolha o que deseja fazer: ', (0, 1))
                    if esco == 1:
                        torrent.parar(qbit, r['hash'])
