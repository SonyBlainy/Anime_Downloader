import os
from path_qbittorrent import caminho_qbit
import psutil
import requests
import subprocess

class Qbit():
    def __init__(self):
        self.api_url = 'http://127.0.0.1:8080/api/v2/'
        self.sessao = self.init_sessao()

    def init_sessao(self):
        if os.path.abspath(r'C:\Program Files\qBittorrent') not in os.environ['Path'].split(os.pathsep):
            os.environ['Path'] += os.pathsep+os.path.abspath(r'C:\Program Files\qBittorrent')
            caminho_qbit()
        lista = [processo.info['name'] for processo in psutil.process_iter(['name'])]
        if not 'qbittorrent.exe' in lista:
            subprocess.run(['powershell', '-NoProfile', '-Command', 'qbittorrent.exe'],
                           encoding='utf-8')
        sessao = requests.Session()
        para = {'username': 'admin', 'password': 'admin123'}
        header = {'Referer': 'http://127.0.0.1:8080'}
        l = sessao.post(self.api_url+'auth/login', data=para, headers=header)
        if l.status_code != 200:
            return None
        return sessao
    
    def baixar(self, ep):
        self.sessao.post(self.api_url+'torrents/add', {'urls': ep.link, 'savepath': ep.caminho})

    def infos(self):
        return self.sessao.get(self.api_url+'torrents/info').json()
    
    def parar(self, hash=None, tudo=False):
        if tudo:
            infos = self.infos()
            for torrent in infos:
                self.sessao.post(self.api_url+'torrents/stop', data={'hashes': torrent['hash']})
                self.sessao.post(self.api_url+'torrents/delete', data={'hashes': torrent['hash'], 'deleteFiles': 'false'})
        else:    
            self.sessao.post(self.api_url+'torrents/stop', data={'hashes': hash})
            self.sessao.post(self.api_url+'torrents/delete', data={'hashes': hash, 'deleteFiles': 'false'})
