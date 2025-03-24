import os
def configurar_diretorios():
    caminhos = {'animes': os.path.join(r'C:\Users', os.getlogin(), 'Desktop', 'Animes'),
                'save': os.path.expandvars(r'%LOCALAPPDATA%\Anime_downloader')}
    for pasta in caminhos.values():
        if not os.path.isdir(pasta):
            os.mkdir(pasta)
    os.environ.update({'caminho': caminhos['animes'], 'save': caminhos['save']})
configurar_diretorios()
import logging
from fera.animes_geral import obter_escolha_valida as ob

class CustomHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            os.startfile('log.log')
            quit()

logging.basicConfig(filename='log.log', filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.addHandler(CustomHandler())
from sakura import Sakura
from fera import animes_geral
from fera import baixando
from bakashi import bakashi_anime
from erai import nyaa
from erai import torrent
from drivee import core
sair = False

while not sair:
    t = 'Download encerrado pelo usuario'
    texto = 'Digite o anime que deseja baixar ou digite sair: '
    nenhum = 'Nenhum anime encontrado'
    print('='*30, 'MENU'.center(30), '='*30, '[1] Pesquisar um anime', '[2] Listar episódios baixados',
          '[3] Qbit', '[0] Sair', sep='\n')
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
            animes = Sakura.pesquisar_anime(nome)
            if not animes:
                logging.warning(nenhum)
                print(nenhum)
                continue
            anime = core.escolher_anime_sakura(animes)
            if not anime:
                continue
            baixando.download_padrao(anime)
            if isinstance(anime.ep, list):
                logging.info('episodios: '+', '.join([ep.nome for ep in anime.ep])+'baixados')
            else:
                logging.info(f'{anime.ep.nome} baixado')
        elif esco == 2:
            nome = str(input('Digite o nome do anime: '))
            animes = bakashi_anime.pesquisar(nome)
            if len(animes) == 0:
                logging.warning(nenhum)
                print(nenhum)
            else:
                print('='*30)
                for i, a in enumerate(animes):
                    print(f'[{i}] {a.nome}')
                esco = ob(texto, (0, len(animes)), True)
                if isinstance(esco, int):
                    anime = animes[esco]
                    anime = bakashi_anime.episodios(anime)
                    anime.listar()
                    if isinstance(anime.ep, list):
                        copia = anime
                        for ep in anime.ep:
                            copia.ep = ep
                            copia.trat()
                            try:
                                baixando.baixarar(copia)
                                logging.info(f'Episodio {copia.ep.nome} baixado')
                            except KeyboardInterrupt:
                                logging.info(t)
                                print(t)
                    else:
                        try:
                            baixando.baixarar(anime)
                            logging.info(f'Episodio {anime.ep.nome} baixado')
                        except KeyboardInterrupt:
                            logging.info(t)
                            print(t)
        elif esco == 3:
            nome = str(input('Digite o nome do anime: '))
            animes = nyaa.pesquisar(nome)
            anime = core.escolher_animes_erai(animes)
            if not anime.ep:
                continue
            else:
                nyaa.baixar_anime(anime)
    elif esco == 2:
        r = animes_geral.listar()
        if r != None:
            if r.site == 'Bakashi':
                anime = bakashi_anime.episodios(r)
                anime.listar()
                if isinstance(anime.ep, list):
                    copia = anime
                    for ep in anime.ep:
                        copia.ep = ep
                        copia.trat()
                        try:
                            baixando.baixarar(copia)
                            logging.info(f'Episodio {copia.ep.nome} baixado')
                        except KeyboardInterrupt:
                            logging.info(t)
                            print(t)
                else:
                    try:
                        baixando.baixarar(anime)
                        logging.info(f'Episodio {anime.ep.nome} baixado')
                    except KeyboardInterrupt:
                        logging.info(t)
                        print(t)
            elif r.site == 'Sakura':
                anime = r
                anime = core.escolher_anime_sakura(anime, True)
                if not anime:
                    continue
                baixando.download_padrao(anime)
                if isinstance(anime.ep, list):
                    logging.info('episodios: '+', '.join([ep.nome for ep in anime.ep])+'baixados')
                else:
                    logging.info(f'{anime.ep.nome} baixado')
            elif r.site.split('_')[0] == 'Erai':
                nome = r.site.split('_')[1].strip()
                anime = nyaa.pesquisar(nome)
                anime = core.escolher_animes_erai(anime)
                if not anime.ep:
                    continue
                else:
                    nyaa.baixar_anime(anime)
    elif esco == 3:
        qbit = torrent.Qbit()
        if not qbit.sessao:
            erro = 'Erro ao fazer login'
            logging.error(erro)
            print(erro)
        else:
            r = qbit.infos()
            if not r:
                n = 'Nenhum torrent encotrado'
                logging.warning(n)
                print(n)
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
                        except:
                            print('Erro! Tente novamente')
                        else:
                            break
                if esco == '00':
                    qbit.parar(tudo=True)
                    logging.info('Todos os torrents encerrados')
                else:
                    print('='*30)
                    r = r[esco]
                    print(f'Nome: {r['name']}', f'Velocidade: {r['dlspeed']/(1024**2):.2f}MB/s',
                          f'Progresso: {r['progress']*100:.2f}%', f'Estado: {r['state']}', sep='\n')
                    print('='*30, '[0] Sair', '[1] Pausar e deletar', sep='\n')
                    esco = ob('Escolha o que deseja fazer: ', (0, 1))
                    if esco == 1:
                        qbit.parar(r['hash'])
                        logging.info(f'Torrent {r['name']} encerrado')
