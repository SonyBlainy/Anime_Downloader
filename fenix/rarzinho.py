import patoolib
import os


def descom(caminho, destino):
    patoolib.extract_archive(caminho, outdir=destino, interactive=False)
    