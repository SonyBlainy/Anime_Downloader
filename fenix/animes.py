import requests
from lxml.html import fromstring
import pickle
from tc.TC import verifica
from fenix.baixando import baixarar
from fenix.renomear import reno
from fenix.rarzinho import descom
import os

path = f"C:\\Users\\{os.getlogin()}\\Desktop\\animes\\"
save = "C:\\Users\\Micro\\AppData\\Local\\Anime_downloader\\"


class Anime:
    def __init__(self, nome, link):
        self.nome = nome
        self.link = link
    def eps(self, ep):
        self.ep = ep
    def listar(self):
        print('='*30)
        for i, ep in enumerate(self.ep):
            print(f'[{i}] {ep.nome}')
        while True:
            try:
                esco = str(input('Escolha qual episódio deseja baixar: '))
                esco = int(esco)
            except:
                if esco.upper() == 'SAIR':
                    break
                elif '-' in esco:
                    break
                else:
                    print('Erro! Tente novamente')
            else:
                if esco >= 0 and esco <= len(self.ep)-1:
                    break
                else:
                    print('Erro! Tente novamente')
        if esco.__class__ == str:
            self.ep = [self.ep[int(ep)] for ep in esco.split('-')]
        else:
            self.ep = self.ep[esco]
    def tratar(self):
        nome = self.nome
        nome = nome.split()
        limpo = []
        for palavra in nome:
            limpo.append(''.join([letra for letra in palavra if letra not in [':', '°', '?', '-']]))
        limpo = '_'.join(limpo)
        self.nome = limpo
        verifica(self)
class Ep:
    def __init__(self, nome, link):
        self.nome = nome
        self.link = link


def pesquisa(anime):
    api = 'https://fenixfansub.net/wp-admin/admin-ajax.php'
    data = {'action': 'ajaxsearchpro_search', 'aspp': anime, 'asid': 2, 'asp_inst_id': '2_1'}
    r = requests.post(api, data)
    r = r.content.decode('utf-8')
    r = fromstring(r)
    animes = r.find_class('asp_content')
    resul = []
    for anime in animes:
        link = anime.xpath('.//a')[1]
        nome = link.text.strip()
        link = link.get('href')
        a = Anime(nome, link)
        resul.append(a)
    return resul

def baixar(anime):
    r = requests.get(anime.ep.link)
    r = fromstring(r.content)
    link = r.xpath('.//div[@id="form-download"]')[0]
    link = link.xpath('input')[0].get('value')
    r = requests.get(link, allow_redirects=False)
    link = r.headers['Location']
    anime.ep.link = link
    anime.ep.caminho = path+anime.nome
    anime.ep.nome = anime.nome+'_'+'_'.join(anime.ep.nome.split())
    baixarar(anime)
    zip(anime)

def zip(anime):
    descom(anime)

def eps(anime):
    r = requests.get(anime.link)
    r = r.content.decode('utf-8')
    r = fromstring(r)
    eps = r.find_class('pt-4')[1]
    eps = eps.find_class('col-md-6')
    resul = []
    for ep in eps:
        nome = ep.xpath('.//span')[0].text
        link = ep.xpath('.//a')[0].get('href')
        e = Ep(nome, link)
        resul.append(e)
    anime.eps(resul)
    return anime 

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
                                with open(save+nome+'\\'+'linkzinho.txt', 'rb') as arquivo:
                                    dados = pickle.load(arquivo)
                            except:
                                print('Erro! Arquivo não existe, baixe um episodio do anime para criar')
                            else:
                                if dados.link.split('.')[1] == 'animestc':
                                    dados.site = 'TC'
                                elif 'sakuraanimes' in dados.link:
                                    dados.site = 'Sakura'
                                elif 'fenixfansub' in dados.link:
                                    dados.site = 'Fenix'
                                return dados
                    else:
                        if 0 <= esc < len(arquivo):
                            os.popen(f'{caminho}\\{arquivo[esc]}')
