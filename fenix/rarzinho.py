import patoolib
import os


def descom(anime):
    patoolib.extract_archive(anime.ep.caminho+f'\\{anime.ep.nome}.rar', outdir=anime.ep.caminho, interactive=False, verbosity=-1)
    for arquivo in os.walk(anime.ep.caminho):
        listinha = arquivo[2]
    for a in listinha:
        if '.rar' in a:
            os.remove(anime.ep.caminho+f'\\{a}')
        elif '[FF]' in a:
            os.rename(anime.ep.caminho+f'\\{a}', anime.ep.caminho+f'\\{anime.ep.nome}.mkv')