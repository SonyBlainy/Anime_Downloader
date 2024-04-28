import gdown
import os

path = f"C:\\Users\\{os.getlogin()}\\Desktop\\animes\\"
save = "C:\\Users\\Micro\\AppData\\Local\\Anime_downloader\\"

def baixar(ep):
    link = ep.link
    link = link.split('/')[-2]
    gdown.download(f'https://drive.google.com/uc?id={link}', f'{ep.caminho}\\{ep.nome}')
