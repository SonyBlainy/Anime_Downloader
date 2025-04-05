import winreg
import os

def caminho_qbit():
    caminho = os.path.abspath(r'C:\Program Files\qBittorrent')
    chave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
    try:
        path_atual, _ = winreg.QueryValueEx(chave, 'Path')
    except FileNotFoundError:
        path_atual = ''
    if not caminho in path_atual.split(os.pathsep):
        caminho = f'{path_atual}{os.pathsep}{caminho}' if path_atual else caminho
        winreg.SetValueEx(chave, 'Path', 0, winreg.REG_EXPAND_SZ, caminho)
    winreg.CloseKey(chave)