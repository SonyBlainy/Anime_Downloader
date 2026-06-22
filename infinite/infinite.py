import os
from httpx import AsyncClient as Client
from bs4 import BeautifulSoup
import re
import asyncio
import time

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'}

async def pesquisar(nome:str):
    if len(nome.split()) > 1:
        nome = '-'.join(nome.split())
    api = f'https://infinitefansub.com/pesquisa/{nome}'
    async with Client(headers=header) as navegador:
        pagina = await navegador.get(api)
        pagina = pagina.content
    pagina = BeautifulSoup(pagina, 'html.parser')
    animes = pagina.select('.anime-list>.anime')
    resultado = []
    for anime in animes:
        link = anime['onclick']
        nome = anime.select_one(':scope>span').text
        link = re.search(r"'(.*)'", link).group(1)
        link = '/'.join(api.split('/')[:-2])+link
        dados = {'nome': nome, 'link': link, 'server': 'Infinite'}
        resultado.append(dados)
    return resultado

async def episodios(link: str):
    async with Client(headers=header) as navegador:
        pagina = await navegador.get(link)
        pagina = pagina.content
    pagina = BeautifulSoup(pagina, 'html.parser')
    eps = pagina.select('.episode-list>.episode-container')
    resultado = {}
    for ep in eps:
        nome = ep.select_one('span').text.split('-')[0]
        nome = nome.split()[-1]
        link = ep.select_one('.episode-links>span:nth-of-type(2)>a')['href']
        resultado[nome] = link
    return resultado

async def baixar(ep, progresso):
    extensao = re.search(r'(\.\w{3})$', ep['link']).group(1)
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
