import os
import logging
import requests

class Qbit():
    def __init__(self):
        self.api_url = 'http://127.0.0.1:8080/api/v2/'
        self.sessao = self.init_sessao()

    def init_sessao(self):
        if 'qbittorrent.exe' not in os.popen('tasklist').read().lower():
            os.system('powershell -Command \"qbittorrent.exe\"')
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
