from httpx import AsyncClient as Client
from bs4 import BeautifulSoup
from urllib.parse import unquote
import re
import asyncio
import os
import time

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'}

async def pesquisar(nome: str) -> list:
    api = 'https://topanimes.net/'
    async with Client(headers=header) as navegador:
        pagina = await navegador.get(api, params={'s': nome})
        pagina = pagina.content
    pagina = BeautifulSoup(pagina, 'html.parser')
    animes = pagina.select_one('.search-page').select('.result-item')
    lista = []
    for a in animes:
        dados = a.select_one('.title>a')
        nome = dados.text
        link = dados.get('href')
        dados = {'nome': nome, 'link': link, 'server': 'TopAnimes'}
        lista.append(dados)
    return lista

async def episodios(link: str):
    async with Client(headers=header) as navegador:
        pagina = await navegador.get(link)
        pagina = pagina.content
    pagina = BeautifulSoup(pagina, 'html.parser')
    eps = pagina.select('.episodios > li')
    data = {}
    for ep in eps:
        nome = ep.select_one('.episodiotitle > a')
        link = nome.get('href')
        nome = re.search(r'Episódio (\d*)', nome.text).group(1)
        data[nome] = link
    limite = asyncio.Semaphore(3)
    data = [player(a, limite) for a in data.items()]
    data = await asyncio.gather(*data, return_exceptions=True)
    data = [i for i in data if not isinstance(i, Exception)]
    return dict(data)

async def player(ep, limite):
    async with limite:
        async with Client(headers=header) as navegador:
            pagina = await navegador.get(ep[1])
            pagina = pagina.content
        pagina = BeautifulSoup(pagina, 'html.parser')
        link = pagina.select_one('#playcontainer')
        link = link.find('iframe', src=re.compile(r'csst.online'))
        if link:
            link = link.get('src')
            if 'topanimes.net' in link:
                link = unquote(link)
                link = re.search(r'\?url=(.*?)&poster', link).group(1)
            async with Client(headers=header) as navegador:
                pagina = await navegador.get(link, follow_redirects=True)
                pagina = pagina.content
            pagina = BeautifulSoup(pagina, 'html.parser')
            js = pagina.select_one('body>script')
            js = js.text
            link = re.findall(r'var player = new Playerjs\(\{([\s\S]*?)\}\);', js)[-1]
            link = re.search(r'\[1080p\](.*?\.mp4)', link).group(1)
        else:
            raise ValueError('Nenhum link válido encontrado')
        return (ep[0], link)

async def baixar(ep, progresso):
    extensao = re.search(r'/\d*(\.\w{3})', ep['link']).group(1)
    caminho = os.path.join(ep['caminho'], ' - '.join(ep['ep'].split())+extensao)
    with open(caminho, 'wb') as arquivo:
        async with Client(headers=header) as navegador:
            async with navegador.stream('GET', ep['link'], follow_redirects=True) as response:
                baixado = 0
                total = int(response.headers['content-length'])
                tempo_utlimo_calculo = time.perf_counter()
                baixado_intervalo = 0
                velocidade_atual = 0
                async for chunck in response.aiter_raw():
                    arquivo.write(chunck)
                    tamanho_chunck = len(chunck)
                    baixado += tamanho_chunck
                    baixado_intervalo += tamanho_chunck
                    tempo_agora = time.perf_counter()
                    delta_tempo = tempo_agora - tempo_utlimo_calculo
                    if delta_tempo > 0.5:
                        velocidade_atual = baixado_intervalo/delta_tempo
                        tempo_utlimo_calculo = tempo_agora
                        baixado_intervalo = 0
                        velocidade_atual /= 1024
                        if velocidade_atual > 1024:
                            velocidade_atual /= 1024
                            velocidade_atual = f'{velocidade_atual:.2f}MB/s'
                        else:
                            velocidade_atual = f'{velocidade_atual:.2f}KB/s'
                    progresso(baixado/total, velocidade_atual)
