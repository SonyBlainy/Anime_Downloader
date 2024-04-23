import logging
logging.basicConfig(filename='log.log', filemode='w', level=logging.CRITICAL)
from fenix import animes as ani
from sakura import Sakura
from tc import TC
from drivee import googledrive as gd
from drivee import trat
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
        print('[1] Fenix Fansub')
        print('[2] Sakura')
        print('[3] AnimesTC')
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
            resul = ani.pesquisa()
            print('='*30)
            if len(resul) == 0:
                print('Nenhum anime encontrado')
            else:
                print(f'Foram encontrados {len(resul)} resultados para sua busca')
                print('='*30)
                for i, r in enumerate(resul):
                    print(f'[{i}] {r["nome"]}')
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
                    eps = ani.eps(resul[escolha])
                    print('='*30)
                    print(f'Foram encontrados {len(eps)} episódios para o anime {resul[escolha]["nome"]}')
                    for i, e in enumerate(eps):
                        print(f'{e["numero"]}')
                    while True:
                        escolha = str(input('Escolha o episódio que deseja baixar ou digite sair: '))
                        try:
                            escolha = int(escolha)
                        except:
                            if '-' in escolha:
                                escolha = [int(e) for e in escolha.split('-') if int(e) > 0 and int(e) <= len(eps)]
                                break
                            else:
                                if escolha.upper() == 'SAIR':
                                    break
                                else:
                                    print('Erro! Tente novamente')
                        else:
                            break
                    if type(escolha) == int:
                        ani.baixar(eps[escolha-1])
                    else:
                        if '-' in escolha:
                            for e in escolha:
                                ani.baixar(eps[e-1])
        elif esco == 2:
            nome = str(input('Digite o nome do anime: '))
            resul = Sakura.pesquisar_anime(nome)
            if resul == []:
                print('Nenhum anime encontrado')
            else:
                print('='*30)
                print(f'Foram encontrados {len(resul)} resultados para sua busca')
                for i, a in enumerate(resul):
                    print(f'[{i}] {a["nome"]}')
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
                    anime = Sakura.listar_episodios(resul[esco])
                    print('='*30)
                    for i, e in enumerate(anime['ep']):
                        print(f'[{i}] {e["nome"]}')
                    while True:
                        try:
                            esco = int(input('Escolha qual episódio deseja baixar: '))
                        except:
                            print('Erro! Tente novamente')
                        else:
                            if esco >= 0 and esco < len(anime['ep']):
                                break
                            else:
                                print('Erro! Opção inválida')
                    anime['ep'] = anime['ep'][esco]
                    Sakura.baixar(anime)
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
                    animes.ep()
                    animes.listar()
                    if type(animes.ep) == list:
                        copia = animes
                        for ep in animes.ep:
                            copia.ep = TC.baixar(ep, varios=True)
                            copia.verificar()
                            copia.baixar()
                    else:
                        animes.ep = TC.baixar(animes.ep)
                        animes.verificar()
                        animes.baixar()
    elif esco == 2:
        r = ani.listar()
        if type(r) == dict:
            if r['site'] == 'Sakura':
                anime = Sakura.listar_episodios(r)
                print('='*30)
                for i, e in enumerate(anime['ep']):
                    print(f'[{i}] {e["nome"]}')
                while True:
                    try:
                        esco = int(input('Escolha qual episódio deseja baixar: '))
                    except:
                        print('Erro! Tente novamente')
                    else:
                        if esco >= 0 and esco < len(anime['ep']):
                            break
                        else:
                            print('Erro! Opção inválida')
                anime['ep'] = anime['ep'][esco]
                Sakura.baixar(anime)
        elif r.site == 'TC':
            r.ep()
            r.listar()
            if type(r.ep) == list:
                copia = r
                for ep in r.ep:
                    copia.ep = TC.baixar(ep, varios=True)
                    copia.verificar()
                    copia.baixar()
            else:
                r.ep = TC.baixar(r.ep)
                r.verificar()
                r.baixar()
