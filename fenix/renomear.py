import os


def reno(caminho, novo):
    for path, dire, arquivo in os.walk(caminho):
        os.rename(path+arquivo[-1], path+novo)
        for a in arquivo:
            if '.rar' in a:
                os.remove(path+a)