import os
def configurar_diretorios():
    caminhos = {'animes': os.path.join(r'C:\Users', os.getlogin(), 'Desktop', 'Animes_teste'),
                'save': os.path.expandvars(r'%LOCALAPPDATA%\Anime_downloader_teste')}
    for pasta in (i for i in caminhos.values()):
        os.makedirs(pasta, exist_ok=True)
    os.environ.update({'caminho': caminhos['animes'], 'save': caminhos['save']})
configurar_diretorios()
from deep_translator import GoogleTranslator as GT
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox
import logging
from PIL import Image
import io
imagem_pesquisar = Image.open('icones\\search.png')
imagem_biblioteca = Image.open('icones\\home.png')
imagem_download = Image.open('icones\\download.png')

class CustomHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            os.startfile('log.log')
            quit()
logging.basicConfig(filename='log.log', filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
logger.addHandler(CustomHandler())
versao = 'v1.0'
from drivee import core

class AnimeDownloaderGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f'Anime Downloader {versao}')
        self.geometry(f'{self.winfo_screenwidth()}x{self.winfo_screenheight()}')
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.state('zoomed')
        self.tradutor = GT(source='en', target='pt')
        self.menu_principal()

    def tela_base(self):
        botoes_frame = ctk.CTkFrame(self.main_frame, fg_color='transparent')
        icone_biblioteca = ctk.CTkImage(imagem_biblioteca, size=(24,24))
        icone_pesquisar = ctk.CTkImage(imagem_pesquisar, size=(24,24))
        icone_download = ctk.CTkImage(imagem_download, size=(24,24))
        anime_texto = ctk.CTkLabel(self.main_frame, text='Anime Downloader', font=('Arial', 18, 'bold'))
        linha_h = ctk.CTkFrame(self.main_frame, height=4, corner_radius=2)
        linha_v = ctk.CTkFrame(self.main_frame, width=4, corner_radius=2)
        pesquisa = ctk.CTkButton(botoes_frame, image=icone_pesquisar,
                                  compound='left', fg_color='transparent', text='Pesquisar', command=self.pesquisar)
        biblioteca = ctk.CTkButton(botoes_frame, image=icone_biblioteca,
                                    compound='left', fg_color='transparent', text='Biblioteca', command=self.menu_principal)
        download = ctk.CTkButton(botoes_frame, image=icone_download,
                                 compound='left', fg_color='transparent', text='Downloads', command=self.downloads)
        anime_texto.pack(pady=20, anchor='w')
        linha_h.pack(fill='x')
        botoes_frame.pack(side='left', anchor='nw')
        pesquisa.pack(pady=5, anchor='nw')
        biblioteca.pack(pady=5, anchor='nw')
        download.pack(pady=5, anchor='nw')
        linha_v.pack(fill='y', padx=5, side='left', anchor='nw')

    def anime_exibir(self, anime_info, anime_poster):
        self.clear_frame()
        self.tela_base()
        anime_info = core.anime_info_pesquisa(anime_info)
        anime_frame = ctk.CTkFrame(self.main_frame)
        anime_frame.pack(expand=True, fill='both', side='left')
        anime_nome = ctk.CTkLabel(anime_frame, text=anime_info.nome, font=('Arial', 18, 'bold'))
        anime_nome.pack(pady=5, padx=5, anchor='nw')
        info_frame_sup = ctk.CTkFrame(anime_frame)
        info_frame_sup.pack(fill='x', anchor='nw')
        anime_poster = ctk.CTkLabel(info_frame_sup, text=None, image=anime_poster, compound='top')
        anime_poster.pack(pady=5, padx=5, anchor='nw', side='left')
        info_anime = ctk.CTkFrame(info_frame_sup)
        info_anime.pack(padx=2, pady=5, anchor='nw', fill='x')
        info_frame_infi = ctk.CTkFrame(anime_frame)
        botao_frame = ctk.CTkFrame(info_frame_sup, fg_color='transparent')
        botao_frame.pack(padx=2, pady=5, fill='x')
        botao_download = ctk.CTkButton(botao_frame, text='Download', command=lambda: self.download_anime(anime_info))
        botao_listar_ep = ctk.CTkButton(botao_frame, text='Listar Episódios', command=lambda: self.listar_ep(anime_info))
        botao_download.pack(padx=2, anchor='nw', side='left')
        botao_listar_ep.pack(padx=2, anchor='nw', side='left')
        data = datetime.strptime(anime_info.info['start_date'], "%Y-%m-%d")
        data = data.strftime("%d/%m/%Y")
        data = ctk.CTkLabel(info_anime, text=f'Data de lançamento: {data}',
                            font=('Arial', 13))
        nota = ctk.CTkLabel(info_anime, text=f'Nota: {anime_info.info['mean']}', font=('Arial', 13))
        genero = [self.tradutor.translate(a['name']) for a in anime_info.info['genres']]
        genero = ctk.CTkLabel(info_anime, text='Genero: '+', '.join(genero))
        status = ctk.CTkLabel(info_anime, text=f'Status: {self.tradutor.translate(' '.join(anime_info.info['status'].split('_')))}')
        n_eps = ctk.CTkLabel(info_anime, text=f'Números de Episódios: {anime_info.info['num_episodes']}')
        info_hora = core.data_info(anime_info.info['broadcast'])
        dia_lancamento = ctk.CTkLabel(info_anime, text=f'Data de exibição: {self.tradutor.translate(info_hora['dia'])} as {info_hora['hora']}')
        season = ctk.CTkLabel(info_anime, text=f'Season: {self.tradutor.translate(anime_info.info['start_season']['season']).capitalize()} de {anime_info.info['start_season']['year']}')
        fonte = ctk.CTkLabel(info_anime, text=f'Fonte: {anime_info.info['source'].capitalize()}')
        nota.pack(pady=2, padx=5, anchor='nw')
        genero.pack(pady=2, padx=5, anchor='nw')
        data.pack(pady=2, padx=5, anchor='nw')
        dia_lancamento.pack(pady=2, padx=5, anchor='nw')
        fonte.pack(pady=2, padx=5, anchor='nw')
        season.pack(pady=2, padx=5, anchor='nw')
        status.pack(pady=2, padx=5, anchor='nw')
        n_eps.pack(pady=2, padx=5, anchor='nw')
        info_frame_infi.pack(pady=5, padx=5, anchor='nw', fill='both', expand=True)
        sinopse = self.tradutor.translate('.'.join(anime_info.info['synopsis'].split('.')[:-1]))
        sinopse = ctk.CTkLabel(info_frame_infi, text=f'Sinopse: {sinopse}', font=('Arial', 14),
                               wraplength=1175)
        sinopse.pack(pady=5, padx=5, anchor='nw')
        #print(anime_info.info)

    def download_anime(self, anime):
        self.clear_frame()
        self.tela_base()
        anime = core.selecionar_ep(anime)
        frame_principal = ctk.CTkFrame(self.main_frame)
        frame_principal.pack(pady=5, padx=5, fill='both', expand=True, anchor='nw')
        frame_anime = ctk.CTkFrame(frame_principal, fg_color='transparent')
        frame_anime.pack(padx=5, pady=5, anchor='nw', fill='x')
        anime_nome = ctk.CTkLabel(frame_anime, text=anime.nome, fg_color='transparent',
                                  font=('Arial', 20, 'bold'))
        anime_nome.pack(anchor='nw', side='left')
        n_eps = ctk.CTkLabel(frame_anime, text=f'{len(anime.ep)} Episódios', font=('Arial', 20, 'bold'))
        n_eps.pack(anchor='ne')
        frame_eps = ctk.CTkFrame(frame_principal, fg_color='transparent')
        frame_eps.pack(padx=5, pady=5, anchor='nw', side='left')
        frame_direita = ctk.CTkFrame(frame_principal, fg_color='transparent')
        frame_direita.pack(anchor='ne')
        botao_download = ctk.CTkButton(frame_direita, text='Baixar eps selecionados', command=lambda: self.baixar_eps(frame_eps, anime))
        botao_download.pack(pady=5, anchor='nw')
        botao_tudo = ctk.CTkButton(frame_direita, text='Baixar todos os eps disponiveis')
        botao_tudo.pack(pady=5, anchor='nw')
        frame_linha = ctk.CTkFrame(frame_eps, fg_color='transparent')
        frame_linha.pack(pady=5, padx=5, anchor='nw')
        for i, ep in enumerate(anime.ep):
            botao_check = ctk.CTkCheckBox(frame_linha, text=ep.nome, font=('Arial', 12))
            botao_check.pack(pady=5, padx=5, anchor='nw', side='left')
            if (i+1)%8 == 0 and i != 0 and i != len(anime.ep)-1:
                frame_linha = ctk.CTkFrame(frame_eps, fg_color='transparent')
                frame_linha.pack(pady=5, padx=5, anchor='nw')
        
    def downloads(self):
        pass

    def baixar_eps(self, frame: ctk.CTkFrame, anime):
        eps = []
        for f in frame.winfo_children():
            for botao in f.winfo_children():
                if botao.get():
                    eps.append(botao.cget('text'))
        eps_baixar = [ep for ep in anime.ep if ep.nome in eps]
        msg = 'Baixando os eps: '+' '.join([ep.nome for ep in eps_baixar])
        messagebox.showinfo('INFO' ,msg)
        

    def listar_ep(self, anime):
        self.clear_frame()
        self.tela_base()

    def pesquisar_anime(self, nome):
        animes = core.pesquisar_tudo(nome)
        self.clear_frame()
        self.tela_base()
        animes_frame = ctk.CTkScrollableFrame(self.main_frame)
        animes_frame.pack(pady=5, fill='both', expand=True, side='left', anchor='nw')
        frame_nome = ctk.CTkFrame(animes_frame, fg_color='transparent')
        frame_nome.pack(fill='x', expand=True)
        try:
            quanti = ctk.CTkLabel(frame_nome, text=f'{len(animes['Erai'])} animes encontrados',
                                  font=('Arial', 18, 'bold'))
        except:
            quanti = ctk.CTkLabel(animes_frame, text='Nenhum anime encontrado', font=('Arial', 18, 'bold'))
            quanti.pack()
        else:
            quanti.pack(anchor='ne')
        if animes['Erai']:
            nome_erai = ctk.CTkLabel(frame_nome, text='Erai', font=('Arial', 18, 'bold'))
            nome_erai.pack(padx=10, anchor='nw', side='left')
            erai_frame = ctk.CTkFrame(animes_frame, fg_color='transparent')
            erai_frame.pack(pady=5, padx=5, anchor='nw', expand=True)
            for i, anime in enumerate(animes['Erai']):
                while True:
                    try:
                        imagem_arquivo = Image.open(io.BytesIO(anime.imagem))
                    except:
                        continue
                    else:
                        break
                comprimento = imagem_arquivo.width//4
                tamanho = (comprimento, imagem_arquivo.height//4)
                imagem = ctk.CTkImage(imagem_arquivo, size=tamanho)
                anime_imagem = ctk.CTkLabel(erai_frame, image=imagem, text=anime.nome,
                                            compound='top', font=('Arial', 14), wraplength=comprimento)
                anime_imagem.pack(pady=10, padx=10, side='left')
                anime_imagem.bind('<Button-1>', lambda event, a=anime, img=imagem: self.anime_exibir(a, img))
                if (i+1)%5 == 0 and i!=0 and i!=len(animes['Erai'])-1:
                    erai_frame = ctk.CTkFrame(animes_frame, fg_color='transparent')
                    erai_frame.pack(pady=5, padx=10, anchor='nw', expand=True)

    def pesquisar(self):
        self.clear_frame()
        self.tela_base()
        barra_pesquisa = ctk.CTkEntry(self.main_frame,
                                      width=200,
                                      height=30,
                                      placeholder_text='Digite o nome do anime...',
                                      corner_radius=20,
                                      fg_color='#FFFFFF',
                                      text_color='#000000',
                                      border_width=1
                                      )
        barra_pesquisa.pack(pady=20)
        barra_pesquisa.bind('<Return>', lambda e: self.pesquisar_anime(barra_pesquisa.get()))
        barra_pesquisa.focus()

    def clear_frame(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

    def menu_principal(self):
        self.clear_frame()
        self.tela_base()

app = AnimeDownloaderGUI()
app.mainloop()
