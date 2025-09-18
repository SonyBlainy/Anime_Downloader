import os
def configurar_diretorios():
    caminhos = {'animes': os.path.join(r'C:\Users', os.getlogin(), 'Desktop', 'Animes'),
                'save': os.path.expandvars(r'%LOCALAPPDATA%\Anime_downloader')}
    for pasta in (i for i in caminhos.values()):
        os.makedirs(pasta, exist_ok=True)
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
versao = 'v0.5.6'
from sakura import Sakura
from fera import animes_geral
from fera import baixando
from fera import update
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
          '[3] Qbit', '[4] Atualizar', '[0] Sair', sep='\n')
    esco = ob('Escolha uma opção: ', (0,4))
    if esco == 0:
        sair = True
    elif esco == 1:
        print('='*30, '[1] Erai', '[2] Sakura', '[3] Bakashi', sep='\n')
        esco = ob('Escolha em qual site deseja pesquisar: ', (1, 3), True)
        if not esco:
            continue
        if esco == 2:
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
        elif esco == 3:
            nome = str(input('Digite o nome do anime: '))
            animes = bakashi_anime.pesquisar(nome)
            if not animes:
                logging.warning(nenhum)
                print(nenhum)
                continue
            animes = [core.Anime(anime['nome'], anime['link']) for anime in animes]
            anime = core.escolher_anime_bakashi(animes)
            if not anime:
                continue
            baixando.download_padrao(anime)
        elif esco == 1:
            nome = str(input('Digite o nome do anime: '))
            animes = nyaa.pesquisar(nome)
            if not animes:
                continue
            anime = core.escolher_animes_erai(animes)
            if not anime:
                continue
            nyaa.baixar_anime(anime)
    elif esco == 2:
        r = animes_geral.listar()
        if r != None:
            if r.site == 'Bakashi':
                anime = r
                anime = core.escolher_anime_bakashi(anime, True)
                if not anime:
                    continue
                baixando.download_padrao(anime)
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
                if not anime:
                    continue
                anime = core.escolher_animes_erai(anime)
                if not anime:
                    continue
                nyaa.baixar_anime(anime)
    elif esco == 3:
        try:
            qbit = torrent.Qbit()
        except Exception as erro:
            logging.error(f'Erro ao iniciar o Qbit: {erro}')
            print('Erro ao iniciar o Qbit')
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
                            if esco.upper() == 'SAIR':
                                break
                            else:
                                print('Erro! Tente novamente')
                        else:
                            break
                if esco == '00':
                    qbit.parar(tudo=True)
                    logging.info('Todos os torrents encerrados')
                if isinstance(esco, int):
                    print('='*30)
                    r = r[esco]
                    print(f'Nome: {r['name']}', f'Velocidade: {r['dlspeed']/(1024**2):.2f}MB/s',
                          f'Progresso: {r['progress']*100:.2f}%', f'Estado: {r['state']}', sep='\n')
                    print('='*30, '[0] Sair', '[1] Pausar e deletar', sep='\n')
                    esco = ob('Escolha o que deseja fazer: ', (0, 1))
                    if esco == 1:
                        qbit.parar(r['hash'])
                        logging.info(f'Torrent {r['name']} encerrado')
    elif esco == 4:
        link = update.atualizar(versao)
        if not link:
            print('O Anime Downloader já está na sua versão mais recente')
