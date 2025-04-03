# Anime Downloader
---
![AnimeGIF](gifs/gif_1.gif)

Um script Python automatizado para baixar episódios de animes de 3 fontes: Sakura, Q1n(antigo Bakashi) e Erai-raws(via Nyaa), além de organizar os arquivos em pastas e gerenciar downloads diretos, e para o Erai, via torrent com integração ao QBittorrent.

---

## Sobre o Projeto

O **Anime Downloader** é uma solução prática e eficiente que automatiza o processo de busca, download e organização de animes. Evitando as repetições de ter que pequisar, baixar, criar pastas e mover arquivos manualmente, caso você goste de organizar os seus animes. Criado para uso pessoal, ele reflete o meu interesse por Python, minha paixão por animes e a minha preguiça com relação a tarefas repetitivas, combinando técnicas avançadas de scraping, manipulação de arquivos e integração com a API do QBittorrent.

---

## Funcionalidades

- **Múltiplas Fontes**: Suporte a downloads de 3 fontes diferentes(sendo o Erai com a melhor qualidade, seguido da Sakura e do Q1n), garantido que existam fontes disponiveis caso uma venha a cair.
- **Organização Automática**: Cria uma pasta chamada animes no seu Desktop, e dentro dela cria pastas para cada anime.
- **Suporte a Torrents**: Integração com a API do QBittorrent para gerenciar downloads torrent.
- **Automação Completa**: Executa todas as etapas – busca, download, organização e execução do arquivo de vídeo – sem intervenção manual, sendo possível baixar multiplos episódios de um mesmo anime simultaneamente.
---
## Como Usar
![GIF](gifs/gif_2.gif)
### Instalação
- Baixe e instale o [Qbittorent](https://qbittorrent.org/download/)

- Baixe e instale o [Python](https://www.python.org/downloads/) junto com o pip

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
- Execute o arquivo `path_qbittorrent.py` como administrador.

### Execução
- Rode o script principal:
   ```bash
   python main.py
   ```
---

## Exemplo de Uso

```bash
$ python main.py
==============================
             MENU
==============================
[1] Pesquisar um anime
[2] Listar episódios baixados
[3] Qbit
[0] Sair
Escolha uma opção: 1
==============================
[1] Sakura
[2] Bakashi
[3] Erai
Escolha em qual site deseja pesquisar: 3
Digite o nome do anime: Ore dake
==============================
[0] Ore dake Level Up na Ken Season 2: Arise from the Shadow
[1] Ore dake Level Up na Ken
[2] Ore dake Haireru Kakushi Dungeon
[3] Ore wo Suki nano wa Omae dake ka yo
[4] Ore ga Suki nano wa Imouto dakedo Imouto ja Nai
Escolha o anime ou digite sair: 0
==============================
[0] Episódio 01
[1] Episódio 02
[2] Episódio 03
[3] Episódio 04
[4] Episódio 05
[5] Episódio 06
[6] Episódio 07
[7] Episódio 08
[8] Episódio 09
[9] Episódio 10
[10] Episódio 11
[11] Episódio 12
[12] Episódio 13
Escolha qual episódio deseja baixar, ou digite sair: 0 
(digite - entre os indices para baixar multiplos episódios simultaneamente)
==============================
             MENU
==============================
[1] Pesquisar um anime
[2] Listar episódios baixados
[3] Qbit
[0] Sair
Escolha uma opção: 3
[0] [Erai-raws] Ore dake Level Up na Ken Season 2: Arise from the Shadow - 01 [1080p CR WEBRip HEVC EAC3][MultiSub][C48A7CB0]
==============================
Escolha um torrent para gerenciar, ou digite 00 para deletar todos os torrents: 0
==============================
Nome: [Erai-raws] Ore dake Level Up na Ken Season 2: Arise from the Shadow - 01 [1080p CR WEBRip HEVC EAC3][MultiSub][C48A7CB0]
Velocidade: 2.55MB/s
Progresso: 2.47%
Estado: downloading
==============================
[0] Sair
[1] Pausar e deletar
Escolha o que deseja fazer:
```

---

## Destaques Técnicos

- **Web Scraping**: Utilza o `requests` para requisições web e `fromstring` do `lxml` para manipulação de arquivos HTML para extrair os dados dos animes e episódios.
- **Gerenciamento de Torrents**: Integração com a API do QBittorrent para adicionar, monitorar e encerrar downloads.
- **Estrutura Modular**: O código é dividido em modulos e classes(`Anime` `Ep` e `Qbit`) para facilitar a manutenção, independência de cada fonte, e expansão de fontes.
---

## Contato

Entre em contato caso encontre bugs:
- **Email**: renangustavo.santos@hotmail.com
- **GitHub**: [SonyBlainy](https://github.com/SonyBlainy)
- **Telegram**: http://t.me/renanhamessi

![GIF](gifs/gif_4.gif)