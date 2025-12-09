# Anime Downloader
---
![AnimeGIF](gifs/gif_1.gif)

Um script Python automatizado para baixar episódios de animes de 3 fontes: Sakura, Q1n(antigo Bakashi) e Erai-raws, além de organizar os arquivos em pastas e gerenciar downloads diretos, e para o Erai, via torrent com integração ao QBittorrent.

---

## Sobre o Projeto

O **Anime Downloader** é uma solução prática e eficiente que automatiza o processo de busca, download e organização de animes. Evitando as repetições de ter que pequisar, baixar, criar pastas e mover arquivos manualmente, caso você goste de organizar os seus animes. Criado para uso pessoal, ele reflete o meu interesse por Python, minha paixão por animes e a minha preguiça com relação a tarefas repetitivas, combinando técnicas avançadas de scraping, manipulação de arquivos e integração com a API do QBittorrent.

---

## Funcionalidades

- **Múltiplas Fontes**: Suporte a downloads de 3 fontes diferentes(sendo o Erai com a melhor qualidade, seguido da Sakura e do Q1n), garantido que existam fontes disponiveis caso uma venha a cair.

- **Organização Automática**: Cria uma pasta chamada animes no seu Desktop, e dentro dela cria pastas para cada anime.

- **Informações Sobre o Anime**: Obtem informações como nota, data de lançamento, hórario de exibição(UTC-3), season, poster, genero, etc, sobre o anime que você pesquisou utilizando a API do MyAnimeList.

- **Suporte a Torrents**: Integração com a API do QBittorrent para gerenciar downloads torrent.

- **Automação Completa**: Executa todas as etapas – busca, download, organização e execução do arquivo de vídeo – sem intervenção manual, sendo possível baixar multiplos episódios de um mesmo anime simultaneamente.
---
## Como Usar
![GIF](gifs/gif_2.gif)
### Instalação
#### Instalação rápida
![GIF](gifs/gif_5.gif)
- Baixe, instale e configure o [Qbittorent](https://qbittorrent.org)

- Recomendo instalar o [VLC](https://www.videolan.org/vlc/index.html) como media player

- Baixe a útima versão do [Anime Downloader](https://github.com/SonyBlainy/Anime_Downloader/releases/latest), execute o instalador e siga todos os passos

#### Instalação Manual

- Baixe e instale o [Qbittorent](https://qbittorrent.org)

- Baixe e instale o [Python](https://www.python.org/downloads/) junto com o pip

- Baixe e instale o [Git](https://git-scm.com/downloads)

- Recomendo instalar o [VLC](https://www.videolan.org/vlc/index.html) como media player

- Clone o repositório:
   ```bash
   git clone https://github.com/SonyBlainy/Anime_Downloader.git
   ```
- Navegue até o diretório:
   ```bash
   cd Anime_Downloader
   ```
- Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### Configuração
![GIF](gifs/gif_3.gif)

- Execute o Qbittorrent, vá em Ferramentas > Opcões > Interface de Usuario da web
- Verifique se a Interface de Usuario da web(Controle Remoto) esta ativada
- Verique se o endereço IP esta como `127.0.0.1` e a porta como `8080`
- Altere o usuário e a senha para `admin` e `admin123` respectivamente

### Execução
- Caso tenha feito a instalação manual, rode o script principal:
   ```bash
   python main.py
   ```
- Se não, execute o atalho na Área de trabalho

---

## Destaques Técnicos

- **Web Scraping**: Utilza o `requests` para requisições web e `lxml` para manipulação de arquivos HTML para extrair os dados dos animes e episódios.
- **Gerenciamento de Torrents**: Integração com a API do QBittorrent para adicionar, monitorar e encerrar downloads.
- **Estrutura Modular**: O código é dividido em modulos e classes(`Anime` `Ep` e `Qbit`) para facilitar a manutenção, independência de cada fonte, e expansão de fontes.
---

## Contato

Entre em contato caso encontre bugs:
- **Email**: renangustavo.santos@hotmail.com
- **GitHub**: [SonyBlainy](https://github.com/SonyBlainy)
- **Telegram**: http://t.me/renanhamessi

![GIF](gifs/gif_4.gif)