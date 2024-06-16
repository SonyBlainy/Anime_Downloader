import gdown

def baixar(ep):
    link = ep.link
    link = link.split('/')[-2]
    gdown.download(f'https://drive.google.com/uc?id={link}', f'{ep.caminho}\\{ep.nome}')
