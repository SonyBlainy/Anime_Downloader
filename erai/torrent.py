import os
import asyncio
from path_qbittorrent import caminho_qbit
import psutil
from httpx import AsyncClient as Client
import subprocess

class Qbit():
    def __init__(self):
        self.api_url = 'http://127.0.0.1:8080/api/v2/'
        self.sessao = None

    async def init_sessao(self):
        if os.path.abspath(r'C:\Program Files\qBittorrent') not in os.environ['Path'].split(os.pathsep):
            os.environ['Path'] += os.pathsep+os.path.abspath(r'C:\Program Files\qBittorrent')
            caminho_qbit()
        lista = [processo.info['name'] for processo in psutil.process_iter(['name'])]
        if not 'qbittorrent.exe' in lista:
            subprocess.run(['powershell', '-NoProfile', '-Command', 'qbittorrent.exe'],
                           encoding='utf-8',
                           creationflags=subprocess.CREATE_NO_WINDOW)
        para = {'username': 'admin', 'password': 'admin123'}
        header = {'Referer': 'http://127.0.0.1:8080'}
        sessao = Client(headers=header)
        l = await sessao.post(self.api_url+'auth/login', data=para, headers=header)
        if l.status_code != 200:
            return None
        self.sessao = sessao
    
    async def baixar(self, ep):
        await self.sessao.post(self.api_url+'torrents/add', data={'urls': ep['link'], 'savepath': ep['caminho']})

    async def infos(self):
        return await self.sessao.get(self.api_url+'torrents/info').json()
    
    async def parar(self, hash=None, tudo=False):
        if tudo:
            infos = await self.infos()
            for torrent in infos:
                await self.sessao.post(self.api_url+'torrents/stop', data={'hashes': torrent['hash']})
                await self.sessao.post(self.api_url+'torrents/delete', data={'hashes': torrent['hash'], 'deleteFiles': 'false'})
        else:    
            await self.sessao.post(self.api_url+'torrents/stop', data={'hashes': hash})
            await self.sessao.post(self.api_url+'torrents/delete', data={'hashes': hash, 'deleteFiles': 'false'})
