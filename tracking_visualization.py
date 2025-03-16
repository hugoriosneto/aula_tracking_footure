# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Visualização de Dados de Rastreamento de Futebol com mplsoccer
#
# Este notebook demonstra como visualizar dados de rastreamento de futebol usando os pacotes `mplsoccer` e `kloppy`. 
#
# ## O que são Dados de Rastreamento?
# 
# Dados de rastreamento capturam as posições de todos os jogadores e da bola no campo, tipicamente a uma taxa de 10-25 vezes por segundo. 
# Diferentemente dos dados de eventos que registram ações discretas (passes, chutes, etc.), dados de rastreamento fornecem informações contínuas sobre os movimentos dos jogadores,
# permitindo-nos analisar:
#
# - Posicionamento dos jogadores e formações
# - Métricas físicas (distância percorrida, sprints, etc.)
# - Padrões táticos e formas de equipe
# - Criação e utilização de espaço
# 
# Neste notebook, vamos trabalhar com dados de rastreamento do PFF FC da Copa do Mundo FIFA 2022 masculina e aprender como:
# 1. Carregar e entender a estrutura de dados de rastreamento
# 2. Visualizar posições de jogadores em momentos específicos
# 3. Criar animações de movimentos de jogadores
# 4. Analisar padrões de movimento dos jogadores

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from kloppy import pff
import mplsoccer
from mplsoccer import Pitch, VerticalPitch
import matplotlib.animation as animation
from IPython.display import HTML
import os
import warnings
warnings.filterwarnings('ignore')

# Definir semente aleatória para reprodutibilidade
np.random.seed(42)

# %% [markdown]
# ## Carregando Dados de Rastreamento com Kloppy
#
# O PFF FC divulgou seus dados de rastreamento de transmissão da Copa do Mundo FIFA 2022. Os conjuntos de dados podem ser solicitados através [deste link](https://www.blog.fc.pff.com/blog/pff-fc-release-2022-world-cup-data).
#
# ### O que é Kloppy?
# 
# `Kloppy` é uma biblioteca Python que nos ajuda a trabalhar com diferentes formatos de dados de futebol. Ela fornece uma maneira padronizada de carregar dados de rastreamento e eventos de vários provedores (como Metrica, Statsbomb, TRACAB e PFF FC). Isso nos poupa de ter que escrever código personalizado para cada formato de dados.
#
# ### Componentes Principais dos Dados:
# - **Dados de Rastreamento**: Os dados de rastreamento são armazenados separadamente por jogo: `{game_id}.jsonl.bz2`
# - **Dados de Eventos**: Os dados de eventos para todos os jogos são armazenados em um único arquivo: `events.json`
# - **Metadados**: As informações de metadados (time da casa, time visitante, data do jogo, etc.). Os metadados de cada jogo são armazenados separadamente como `{game_id}.json`.
# - **Elencos**: Os elencos contêm informações sobre as escalações dos times. Os elencos de cada jogo são armazenados separadamente como `{game_id}.json`.
#
# ### Carregando os Dados
#
# Para carregar os dados de rastreamento como um TrackingDataset, usamos a função `load_tracking()` do módulo `pff` em kloppy.
#
# **Parâmetros necessários:**
# - `meta_data`: Caminho contendo metadados sobre os dados de rastreamento.
# - `roster_meta_data`: Caminho contendo metadados do elenco, como detalhes dos jogadores.
# - `raw_data`: Caminho contendo os dados brutos de rastreamento.
#
# **Parâmetros opcionais:**
# - `coordinates`: O sistema de coordenadas a ser usado para os dados de rastreamento (ex: "pff").
# - `sample_rate`: A taxa de amostragem para reduzir os dados. Se None, nenhuma redução é aplicada.
# - `limit`: O número máximo de registros a serem processados. Se None, todos os registros são processados.
# - `only_alive`: Se deve incluir apenas sequências quando a bola está em jogo.

# %%
# Carregar os dados de rastreamento
# Ajuste os caminhos dos arquivos baseado na localização dos seus dados
dataset = pff.load_tracking(
    meta_data="data/pff_metadata_10517.json",
    roster_meta_data="data/pff_rosters_10517.json",
    raw_data="data/pff_10517.jsonl.bz2",
    # Parâmetros Opcionais
    coordinates="pff",
    sample_rate=None,
    limit=None
)

# Converter para DataFrame para manipulação mais fácil
df = dataset.to_df()

# %% [markdown]
# ## Exploração Básica dos Dados
#
# Antes de mergulhar nas visualizações, vamos explorar nossos dados de rastreamento para entender com o que estamos trabalhando.
# Este é um primeiro passo essencial em qualquer projeto de ciência de dados!

# %%
# Vamos primeiro olhar para as primeiras linhas dos dados
print("Primeiras 5 linhas dos nossos dados de rastreamento:")
print(df.head())

# %%
# Verificar a forma do nosso DataFrame - quantas linhas (frames) e colunas temos?
print(f"Forma do DataFrame: {df.shape} (linhas, colunas)")

# %%
# Quais colunas estão disponíveis em nosso conjunto de dados?
print("Nomes das colunas:")
for i, col in enumerate(df.columns):
    print(f"{i+1}. {col}")

# %%
# Vamos obter algumas estatísticas básicas sobre nossos dados
print("Estatísticas básicas para coordenadas da bola:")
print(df[['ball_x', 'ball_y', 'ball_z']].describe())

# %%
# Quantos períodos existem na partida?
periods = df['period_id'].unique()
print(f"Períodos na partida: {periods}")

# Verificar quantos frames temos por período
print("\nFrames por período:")
for period in periods:
    count = len(df[df['period_id'] == period])
    print(f"Período {period}: {count} frames")

# %%
# Vamos examinar quando a bola está em jogo vs. parada
ball_states = df['ball_state'].value_counts()
print("Distribuição de estados da bola:")
print(ball_states)

# Calcular a porcentagem de tempo que a bola está em jogo
in_play_pct = ball_states.get('alive', 0) / len(df) * 100
print(f"\nPorcentagem de tempo que a bola está em jogo: {in_play_pct:.2f}%")

# %% [markdown]
# ### Entendendo a Estrutura dos Dados
#
# Nossos dados de rastreamento contêm coordenadas para cada jogador e a bola em cada timestamp. Aqui está o que as principais colunas representam:
# 
# - `period_id`: O período da partida (1º tempo, 2º tempo, etc.)
# - `timestamp`: Tempo em segundos desde o início do período
# - `frame_id`: Identificador único para cada quadro de dados
# - `ball_state`: Indica se a bola está 'alive' (em jogo) ou 'dead' (fora de jogo)
# - `ball_owning_team_id`: ID do time em posse da bola
# - `ball_x`, `ball_y`, `ball_z`: Coordenadas 3D da bola
# - Coordenadas dos jogadores: Colunas como `{player_id}_x`, `{player_id}_y` com posições 2D de cada jogador
# 
# As coordenadas usam um sistema de coordenadas padrão de campo de futebol:
# - eixo-x: ao longo do comprimento do campo (gol a gol)
# - eixo-y: ao longo da largura do campo (linha lateral a linha lateral)
# - Para dados PFF, as dimensões do campo são aproximadamente 72 x 36 em seu sistema de coordenadas

# %%
# Informações básicas sobre a partida a partir dos metadados
home_team = next(team.name for team in dataset.metadata.teams if str(team.ground) == "home")
away_team = next(team.name for team in dataset.metadata.teams if str(team.ground) == "away")
home_team_id = next(team.team_id for team in dataset.metadata.teams if str(team.ground) == "home")
away_team_id = next(team.team_id for team in dataset.metadata.teams if str(team.ground) == "away")

print(f"Partida: {home_team} (ID: {home_team_id}) vs {away_team} (ID: {away_team_id})")
print(f"Total de frames: {len(df)}")
print(f"Períodos: {df['period_id'].unique()}")
print(f"Intervalo de tempo: {df['timestamp'].min()} a {df['timestamp'].max()} segundos")

# %% [markdown]
# ## Processamento de Dados e Identificação de Jogadores
#
# Para visualizar as posições dos jogadores, precisamos identificar quais colunas correspondem a quais jogadores.
# Isso requer algum processamento de dados:
#
# 1. Extrair IDs de jogadores a partir dos nomes das colunas
# 2. Combinar esses IDs com informações de jogadores dos metadados
# 3. Separar jogadores em seus respectivos times
#
# Esta é uma tarefa comum de manipulação de dados em análises esportivas!

# %%
# PASSO 1: Extrair IDs de jogadores a partir dos nomes das colunas
# Procuramos por colunas terminando com '_x' que não são a bola
player_cols = [col for col in df.columns if '_x' in col and 'ball' not in col]
print(f"Encontradas {len(player_cols)} colunas de coordenadas de jogadores")
print(f"Colunas de exemplo: {player_cols[:3]}...")

# Extrair apenas os IDs de jogadores desses nomes de colunas
player_ids = [int(col.split('_')[0]) for col in player_cols]
print(f"Extraídos {len(player_ids)} IDs de jogadores únicos")

# %%
# PASSO 2: Obter informações dos jogadores a partir dos metadados do conjunto de dados
player_info = {}
for team in dataset.metadata.teams:
    team_id = team.team_id
    team_name = team.name
    for player in team.players:
        player_id = int(player.player_id)
        if player_id in player_ids:
            player_info[player_id] = {
                'name': player.name,
                'jersey_no': player.jersey_no,
                'team_id': team_id,
                'team_name': team_name,
                'position': player.starting_position
            }

# Vamos ver informações de um jogador como exemplo
print("Informações de exemplo de um jogador:")
example_player_id = list(player_info.keys())[0]
print(f"ID do Jogador: {example_player_id}")
for key, value in player_info[example_player_id].items():
    print(f"  {key}: {value}")

# %%
# Converter o dicionário player_info em um DataFrame
players_df = pd.DataFrame.from_dict(player_info, orient='index').reset_index()
players_df.rename(columns={'index': 'player_id'}, inplace=True)

# Ordenar por team_name e jersey_no para melhor legibilidade
players_df = players_df.sort_values(['team_name', 'jersey_no'])

# Exibir o DataFrame
print(f"DataFrame criado com {len(players_df)} jogadores")
print(players_df.head())

# Estatísticas rápidas sobre jogadores por time
print("\nJogadores por time:")
print(players_df['team_name'].value_counts())

# Estatísticas rápidas sobre posições
print("\nJogadores por posição:")
print(players_df['position'].value_counts())

# %%
# PASSO 3: Criar listas separadas para jogadores da casa e visitantes
home_players = [player_id for player_id, info in player_info.items() if info['team_id'] == home_team_id]
away_players = [player_id for player_id, info in player_info.items() if info['team_id'] == away_team_id]

print(f"Time da casa ({home_team}) tem {len(home_players)} jogadores")
print(f"Time visitante ({away_team}) tem {len(away_players)} jogadores")

# Exibir alguns jogadores de cada time (nome e número da camisa)
print("\nAlguns jogadores do time da casa:")
for p in home_players[:5]:
    print(f"  {player_info[p]['name']} (#{player_info[p]['jersey_no']}) - {player_info[p]['position']}")

print("\nAlguns jogadores do time visitante:")
for p in away_players[:5]:
    print(f"  {player_info[p]['name']} (#{player_info[p]['jersey_no']}) - {player_info[p]['position']}")

# %% [markdown]
# ### Exercício para Estudantes
# 
# Tente responder a estas perguntas usando os dados que processamos:
# 
# 1. Quantos goleiros existem no conjunto de dados? (Dica: Observe o campo 'position')
# 2. Qual é a distribuição de posições de jogadores em cada time?
# 3. Encontre o jogador com o maior número de camisa na partida
# 
# (Você pode escrever código em uma nova célula para responder a estas perguntas)

# %% [markdown]
# ## Visualizando um Único Frame
#
# Agora vamos visualizar como são as posições dos jogadores em um momento específico da partida.
# Vamos usar o pacote `mplsoccer`, que fornece ferramentas de visualização específicas para futebol.
#
# ### O que é mplsoccer?
# 
# `mplsoccer` é uma biblioteca Python construída sobre matplotlib que fornece funções de plotagem específicas para futebol.
# Ela torna muito mais fácil criar visualizações de futebol com:
# - Campos de futebol pré-configurados com dimensões e marcações corretas
# - Ferramentas para plotar posições de jogadores, passes, chutes, etc.
# - Suporte para visualizações de dados de rastreamento e eventos

# %%
# Vamos criar uma função para visualizar um único frame de dados de rastreamento
def plot_frame(frame_data, title=None, ax=None, show_player_labels=True):
    """
    Plota um único frame de dados de rastreamento usando mplsoccer.
    
    Parâmetros:
    -----------
    frame_data : pandas.Series
        Uma única linha do dataframe de rastreamento contendo posições de jogadores e da bola
    title : str, opcional
        Título para o gráfico
    ax : matplotlib.axes.Axes, opcional
        Eixos para plotar. Se None, cria uma nova figura e eixos.
    show_player_labels : bool, padrão=True
        Se deve mostrar os números das camisas dos jogadores
        
    Retorna:
    --------
    fig : matplotlib.figure.Figure
        A figura contendo o gráfico
    ax : matplotlib.axes.Axes
        Os eixos contendo o gráfico
    """
    # Criar uma nova figura e eixos se não fornecidos
    if ax is None:
        # Criar um campo com fundo de grama e linhas brancas
        pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68)
        fig, ax = pitch.draw(figsize=(12, 8))
    else:
        pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68)
        fig = ax.figure
        pitch.draw(ax=ax)
    
    # Extrair posição da bola dos dados do frame
    ball_x = frame_data['ball_x']
    ball_y = frame_data['ball_y']
    
    # Dimensionar o tamanho da bola baseado na altura (se disponível)
    # Valor maior significa que a bola está mais alta do chão
    ball_size = 12
    
    # Plotar a bola como um círculo branco com contorno preto
    pitch.scatter(ball_x, ball_y, s=ball_size, color='white', edgecolors='black', zorder=20, ax=ax)
    
    # Plotar jogadores do time da casa (círculos azuis)
    for player_id in home_players:
        x_col = f"{player_id}_x"
        y_col = f"{player_id}_y"
        
        # Plotar apenas se as coordenadas do jogador existirem e não forem NaN
        if x_col in frame_data and y_col in frame_data and not pd.isna(frame_data[x_col]) and not pd.isna(frame_data[y_col]):
            player_x = frame_data[x_col]
            player_y = frame_data[y_col]
            jersey_num = player_info[player_id]['jersey_no']
            
            # Desenhar o jogador como um círculo azul
            pitch.scatter(player_x, player_y, s=120, color='blue', edgecolors='white', zorder=10, ax=ax)
            
            # Adicionar o número da camisa do jogador dentro do círculo
            if show_player_labels:
                ax.text(player_x, player_y, str(jersey_num), color='white', fontsize=8, 
                        ha='center', va='center', zorder=15)
    
    # Plotar jogadores do time visitante (círculos vermelhos)
    for player_id in away_players:
        x_col = f"{player_id}_x"
        y_col = f"{player_id}_y"
        
        # Plotar apenas se as coordenadas do jogador existirem e não forem NaN
        if x_col in frame_data and y_col in frame_data and not pd.isna(frame_data[x_col]) and not pd.isna(frame_data[y_col]):
            player_x = frame_data[x_col]
            player_y = frame_data[y_col]
            jersey_num = player_info[player_id]['jersey_no']
            
            # Desenhar o jogador como um círculo vermelho
            pitch.scatter(player_x, player_y, s=120, color='red', edgecolors='white', zorder=10, ax=ax)
            
            # Adicionar o número da camisa do jogador dentro do círculo
            if show_player_labels:
                ax.text(player_x, player_y, str(jersey_num), color='white', fontsize=8, 
                        ha='center', va='center', zorder=15)
    
    # Adicionar título se fornecido
    if title:
        ax.set_title(title, fontsize=16)
    
    # Adicionar nomes dos times nos cantos do campo
    ax.text(-50, -32, home_team, color='blue', fontsize=12, ha='left', va='top', weight='bold')
    ax.text(50, -32, away_team, color='red', fontsize=12, ha='right', va='top', weight='bold')
    
    return fig, ax

# %%
# Vamos visualizar um único frame da partida
# Primeiro, vamos escolher um frame onde a bola está em jogo ('alive')
frames_with_ball_in_play = df[df['ball_state'] == 'alive']
print(f"Existem {len(frames_with_ball_in_play)} frames com a bola em jogo")

# Selecionar um frame em torno do 30º frame com a bola em jogo
frame_index = frames_with_ball_in_play.iloc[30].name
frame = df.loc[frame_index]

# Obter o timestamp e informações do frame para o título
timestamp = frame['timestamp']
frame_id = frame['frame_id']
title = f"Período: {frame['period_id']} | Tempo: {timestamp} | Frame: {frame_id}"

# Plotar o frame
fig, ax = plot_frame(frame, title=title)
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Criando uma Animação de Sequência
#
# Visualizações estáticas são úteis, mas animações podem nos dar uma compreensão muito melhor do movimento dos jogadores ao longo do tempo.
# Vamos criar uma animação de uma sequência de frames para visualizar como os jogadores e a bola se movem durante o jogo.
#
# Vamos usar o módulo de animação do Matplotlib, que nos permite criar animações quadro a quadro.

# %%
# Definir uma função para criar animações a partir de nossos dados de rastreamento
# %%
# Definir uma função para criar animações a partir de nossos dados de rastreamento
def create_animation(df, start_frame, num_frames=100, fps=10, show_player_labels=True, save_path=None, format='html'):
    """
    Criar uma animação a partir de dados de rastreamento.
    
    Parâmetros:
    -----------
    df : pandas.DataFrame
        DataFrame contendo dados de rastreamento
    start_frame : int
        Índice de frame inicial ou frame_id
    num_frames : int, padrão=100
        Número de frames para animar
    fps : int, padrão=10
        Frames por segundo na animação
    show_player_labels : bool, padrão=True
        Se deve mostrar os números das camisas dos jogadores
    save_path : str, opcional
        Caminho para salvar a animação (None para não salvar)
    format : str, padrão='html'
        Formato para salvar a animação ('html', 'gif', 'mp4')
        
    Retorna:
    --------
    Objeto de animação ou objeto de exibição HTML
    """
    # Configurar a figura e o campo
    pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68)
    fig, ax = pitch.draw(figsize=(12, 8))
    
    # Encontrar o índice de início correto em nosso dataframe
    # Isso lida se passamos um número de frame ou índice
    if isinstance(start_frame, int) and start_frame >= 0 and start_frame < len(df):
        start_idx = start_frame
    else:
        # Se frame_id é fornecido, encontre seu índice
        mask = df['frame_id'] == start_frame
        if mask.any():
            start_idx = df[mask].index[0]
        else:
            start_idx = 0
            print(f"Aviso: Frame {start_frame} não encontrado. Começando do início.")
    
    # Extrair a sequência de frames para animar
    end_idx = min(start_idx + num_frames, len(df))
    frames_to_animate = df.iloc[start_idx:end_idx]
    
    # Inicializar o objeto de texto do título
    title_text = ax.text(36, 38, "", fontsize=14, ha='center', va='center')
    
    # Função de atualização da animação - chamada para cada frame
    def update(frame_idx):
        # Limpar os eixos para o novo frame
        ax.clear()
        pitch.draw(ax=ax)
        
        # Obter os dados do frame atual
        frame_data = frames_to_animate.iloc[frame_idx]
        
        # Obter o timestamp e id do frame para o título
        timestamp = frame_data['timestamp']
        frame_id = frame_data['frame_id']
        period = frame_data['period_id']
        
        # Criar e atualizar o título
        title = f"Período: {period} | Tempo: {timestamp} | Frame: {frame_id}"
        ax.set_title(title, fontsize=16)
        
        # Plotar o frame
        plot_frame(frame_data, ax=ax, show_player_labels=show_player_labels)
        
        # Retornar uma lista vazia (necessário para alguns métodos de animação)
        return []
    
    # Criar a animação - isso chama a função update() para cada frame
    anim = animation.FuncAnimation(fig, update, frames=len(frames_to_animate), 
                                   interval=1000/fps, blit=False)
    
    # Salvar a animação se um caminho for fornecido
    if save_path:
        if format.lower() == 'gif':
            anim.save(save_path, writer='pillow', fps=fps, dpi=80)
            return anim
        elif format.lower() == 'mp4':
            # Tentar usar o escritor ffmpeg se disponível, caso contrário usar HTML
            try:
                Writer = animation.writers['ffmpeg']
                writer = Writer(fps=fps, metadata=dict(artist='Me'), bitrate=1800)
                anim.save(save_path, writer=writer, dpi=150)
                return anim
            except:
                print("FFmpeg não disponível. Alternando para saída HTML.")
                # Padrão para HTML se FFmpeg não estiver disponível
                html_obj = HTML(anim.to_jshtml())
                return html_obj
        else:  # Padrão para HTML
            html_obj = HTML(anim.to_jshtml())
            return html_obj
    
    # Se não houver caminho de salvamento, retornar HTML para exibição no notebook
    return HTML(anim.to_jshtml())

# %% [markdown]
# Agora vamos criar uma animação para uma sequência de frames.
# Vamos encontrar um período interessante quando a bola está em jogo.

# %%
# Encontrar todos os frames onde a bola está em jogo
alive_sequences = df[df['ball_state'] == 'alive']

# Vamos começar a partir do 100º frame onde a bola está viva
# Este deve ser um momento interessante na partida
start_idx = alive_sequences.index[100]

# Criar a animação - 100 frames a 10 frames por segundo
animation_html = create_animation(df, start_idx, num_frames=100, fps=10, 
                                 show_player_labels=True, format='html')

# Exibir a animação no notebook
animation_html

# %% [markdown]
# ### Análise da Animação
# 
# Tire um tempo para observar a animação:
# 
# - Como os times mantêm suas formações enquanto se movem?
# - Como os jogadores reagem ao movimento da bola?
# - Você consegue identificar algum padrão tático na forma como os jogadores se movem?
# - Quais jogadores fazem os movimentos mais significativos?
# 
# Estes são os tipos de perguntas que os dados de rastreamento nos ajudam a responder!

# %% [markdown]
# ## Salvando Animações em Diferentes Formatos
#
# Agora vamos demonstrar como salvar nossas animações em diferentes formatos: GIF, MP4 e HTML.

# %%
# Criar diretório para arquivos de saída se não existir
output_dir = "animations"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Definir frame inicial e número de frames para animar
start_idx = alive_sequences.index[200]  # Ponto de partida diferente
num_frames = 50  # Menos frames para processamento mais rápido

# Salvar como GIF
gif_path = os.path.join(output_dir, "tracking_animation.gif")
create_animation(df, start_idx, num_frames=num_frames, fps=10, 
                save_path=gif_path, format='gif')
print(f"GIF salvo em {gif_path}")

# Salvar como MP4 (se ffmpeg estiver disponível)
mp4_path = os.path.join(output_dir, "tracking_animation.mp4")
try:
    create_animation(df, start_idx, num_frames=num_frames, fps=10, 
                    save_path=mp4_path, format='mp4')
    print(f"MP4 salvo em {mp4_path}")
except Exception as e:
    print(f"Não foi possível salvar MP4: {e}")

# Salvar como HTML
html_path = os.path.join(output_dir, "tracking_animation.html")
html_anim = create_animation(df, start_idx, num_frames=num_frames, fps=10, format='html')

# Salvar o HTML em um arquivo
with open(html_path, "w") as f:
    f.write(html_anim.data)
print(f"HTML salvo em {html_path}")

# %% [markdown]
# ## Visualização Avançada: Rastreamento de Trajetórias de Jogadores
#
# Vamos criar uma visualização mais avançada que mostra as trajetórias de movimento dos jogadores ao longo do tempo.
# Isso é útil para analisar:
# 
# - Padrões de movimento dos jogadores
# - Cobertura defensiva
# - Corridas de ataque
# - Criação de espaço
# 
# Vamos plotar o caminho que cada jogador percorre ao longo de uma sequência de frames, o que nos
# dá insights sobre seus padrões de movimento durante uma fase específica do jogo.

# %%
def plot_player_paths(df, start_frame, num_frames=50, player_ids=None, include_ball=True):
    """
    Plotar trajetórias de movimento dos jogadores ao longo de uma sequência de frames.
    
    Parâmetros:
    -----------
    df : pandas.DataFrame
        DataFrame contendo dados de rastreamento
    start_frame : int
        Índice de frame inicial ou frame_id
    num_frames : int, padrão=50
        Número de frames para visualizar
    player_ids : list, opcional
        Lista de IDs de jogadores para rastrear (None para todos os jogadores)
    include_ball : bool, padrão=True
        Se deve incluir a trajetória da bola
    
    Retorna:
    --------
    fig : matplotlib.figure.Figure
        A figura contendo o gráfico
    ax : matplotlib.axes.Axes
        Os eixos contendo o gráfico
    """
    # Configurar a figura e o campo - combinar com o mesmo tipo de campo que create_animation
    pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68)
    fig, ax = pitch.draw(figsize=(12, 8))
    
    # Encontrar o índice de início correto em nosso dataframe - usar a mesma lógica que create_animation
    if isinstance(start_frame, int) and start_frame >= 0 and start_frame < len(df):
        start_idx = start_frame
    else:
        # Se frame_id é fornecido, encontre seu índice
        mask = df['frame_id'] == start_frame
        if mask.any():
            start_idx = df[mask].index[0]
        else:
            start_idx = 0
            print(f"Aviso: Frame {start_frame} não encontrado. Começando do início.")
    
    # Extrair a sequência de frames para visualizar
    end_idx = min(start_idx + num_frames, len(df))
    sequence_df = df.iloc[start_idx:end_idx].copy()
    
    # Se nenhum jogador específico for especificado, use todos os jogadores
    if player_ids is None:
        # Combinar jogadores da casa e visitantes
        player_ids = home_players + away_players
    
    # Obter primeiro e último frames para referência
    first_frame = sequence_df.iloc[0]
    last_frame = sequence_df.iloc[-1]
    
    # Plotar trajetória da bola se include_ball for True
    if include_ball:
        # Obter coordenadas da bola para cada frame
        ball_x = sequence_df['ball_x'].values
        ball_y = sequence_df['ball_y'].values
        
        # Plotar pequenos pontos brancos ao longo da trajetória da bola
        pitch.scatter(ball_x, ball_y, alpha=0.3, s=10, color='white', zorder=5, ax=ax)
        
        # Usar ax.plot em vez de pitch.lines para desenhar uma linha contínua
        ax.plot(ball_x, ball_y, lw=2, color='white', alpha=0.6, zorder=6)
        
        # Marcar posição inicial com círculo e posição final com estrela
        pitch.scatter(ball_x[0], ball_y[0], s=120, color='white', edgecolors='black', 
                     marker='o', zorder=7, ax=ax, label='Início')
        pitch.scatter(ball_x[-1], ball_y[-1], s=120, color='white', edgecolors='black', 
                     marker='*', zorder=7, ax=ax, label='Fim')
    
    # Plotar trajetória para cada jogador
    for player_id in player_ids:
        x_col = f"{player_id}_x"
        y_col = f"{player_id}_y"
        
        # Verificar se os dados do jogador existem e não são todos NaN
        if x_col in sequence_df.columns and y_col in sequence_df.columns and \
           not sequence_df[x_col].isna().all() and not sequence_df[y_col].isna().all():
            
            # Obter posições do jogador, eliminando valores NaN (momentos em que o jogador não foi rastreado)
            player_df = sequence_df[[x_col, y_col]].dropna()
            if len(player_df) < 2:  # Pular se não houver pontos suficientes para desenhar uma trajetória
                continue
                
            # Obter todas as posições x e y para este jogador
            x_values = player_df[x_col].values
            y_values = player_df[y_col].values
            
            # Definir cor com base no time do jogador
            is_home = player_id in home_players
            color = 'blue' if is_home else 'red'
            jersey_num = player_info[player_id]['jersey_no']
            
            # Plotar pequenos pontos ao longo da trajetória do jogador
            pitch.scatter(x_values, y_values, alpha=0.3, s=10, color=color, zorder=5, ax=ax)
            
            # Conectar os pontos com uma linha
            ax.plot(x_values, y_values, lw=2, color=color, alpha=0.6, zorder=6)
            
            # Adicionar número da camisa ao final
            ax.text(x_values[-1], y_values[-1], str(jersey_num), color='white', fontsize=8, 
                    ha='center', va='center', zorder=9)
    
    # Obter timestamp inicial e final para o título
    start_time = sequence_df.iloc[0]['timestamp']
    end_time = sequence_df.iloc[-1]['timestamp']
    period = sequence_df.iloc[0]['period_id']
    
    # Adicionar informações de partida e tempo
    title = f"{home_team} vs {away_team}\nPeríodo {period}: {start_time:.1f}s a {end_time:.1f}s ({num_frames} frames)"
    ax.set_title(title, fontsize=14)
    
    # Adicionar nomes dos times nos cantos do campo
    ax.text(-50, -32, home_team, color='blue', fontsize=12, ha='left', va='top', weight='bold')
    ax.text(50, -32, away_team, color='red', fontsize=12, ha='right', va='top', weight='bold')
    
    # Adicionar legenda
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), frameon=False, ncol=2)
    
    plt.tight_layout()
    return fig, ax

# %%
# Vamos visualizar trajetórias de jogadores ao longo de uma sequência
# Começar do frame 300 onde a bola está em jogo
start_idx = alive_sequences.index[300]
num_frames = 100  # Mostrar movimento sobre 10 segundos (10 fps)

# Visualizar trajetórias para todos os jogadores
fig, ax = plot_player_paths(df, start_idx, num_frames=num_frames, include_ball=True)
plt.show()

# %% [markdown]
# ### Análise de Padrões de Movimento
# 
# A visualização acima mostra as trajetórias que cada jogador percorreu ao longo de cerca de 10 segundos.
# 
# Vamos agora nos concentrar em alguns jogadores-chave para analisar seus movimentos mais claramente:

# %%
# Vamos selecionar alguns jogadores para focar
# Escolheremos 3 jogadores de cada time
home_sample = home_players[:3]  # Primeiros 3 jogadores do time da casa
away_sample = away_players[:3]  # Primeiros 3 jogadores do time visitante

# Obter seus nomes e números
print("Jogadores selecionados do time da casa:")
for p in home_sample:
    print(f"  {player_info[p]['name']} (#{player_info[p]['jersey_no']}) - {player_info[p]['position']}")

print("\nJogadores selecionados do time visitante:")
for p in away_sample:
    print(f"  {player_info[p]['name']} (#{player_info[p]['jersey_no']}) - {player_info[p]['position']}")

# Plotar trajetórias para apenas esses jogadores
selected_players = home_sample + away_sample
fig, ax = plot_player_paths(df, start_idx, num_frames=num_frames, 
                           player_ids=selected_players, include_ball=True)
plt.show()

# %% [markdown]
# ### Exercício para Estudantes
# 
# Tente responder a estas perguntas:
# 
# 1. Selecione e visualize as trajetórias de movimento apenas dos jogadores atacantes de ambos os times
# 2. Encontre uma sequência onde há muita movimentação da bola e visualize a reação dos jogadores
# 3. Compare os padrões de movimento entre defensores e meio-campistas
# 4. Você consegue identificar algum jogador que cobre a maior distância em uma sequência de 10 segundos?

# %% [markdown]
# ## Explorando um Momento Tático: Messi no Terceiro Terceiro
#
# Um dos aspectos mais interessantes dos dados de rastreamento é a capacidade de isolar situações específicas táticas.
# Nesta seção, vamos nos concentrar em momentos quando Lionel Messi está no terceiro terceiro da área de campo.
#
# O terceiro terceiro é uma área crítica onde jogadores como Messi podem criar oportunidades de gol.
# Ao analisar esses momentos, podemos entender:
#
# - Posicionamento de Messi em áreas perigosas
# - Como os companheiros de equipe se posicionam ao redor dele
# - Resposta defensiva dos oponentes
# - Padrões em seu movimento em situações de ataque

# %%
# Primeiro, vamos encontrar Messi em nosso conjunto de dados de jogadores
# Nota: Este é um espaço reservado - você precisará verificar se Messi está neste conjunto de dados
messi_id = None

# Procurar Messi em nosso dicionário player_info
for player_id, info in player_info.items():
    if "Messi" in info['name']:
        messi_id = player_id
        print(f"Encontrado Messi! ID do jogador: {messi_id}")
        print(f"Time: {info['team_name']}, Camisa: {info['jersey_no']}, Posição: {info['position']}")
        break

# Se Messi não for encontrado neste jogo, use um jogador substituto
# Você pode substituir com outro jogador estelar deste jogo
if messi_id is None:
    print("Messi não encontrado neste conjunto de dados. Você pode substituir com outro jogador.")
    # Para demonstração, usaremos o primeiro atacante que encontrarmos
    for player_id, info in player_info.items():
        if info['position'] in ['CF', 'RW', 'LW', 'ST', 'SS', 'FW']:
            messi_id = player_id
            print(f"Usando {info['name']} (#{info['jersey_no']}) como substituto.")
            break

# %% [markdown]
# ## Conclusão
#
# Neste notebook, demonstramos como:
#
# 1. Carregar dados de rastreamento do PFF FC usando kloppy
# 2. Processar e organizar informações sobre jogadores e times
# 3. Visualizar posições de jogadores em momentos específicos
# 4. Criar animações de movimentos de jogadores
# 5. Exportar visualizações em vários formatos (GIF, MP4, HTML)
# 6. Criar visualizações avançadas de rastreamento de trajetórias de jogadores
#
# Essas técnicas podem ser aplicadas para analisar movimentos, táticas e jogadas específicas de dados de rastreamento de futebol. 

# %%
# Definir o "terceiro terceiro" no sistema de coordenadas
# Para dados PFF com dimensões de campo aproximadamente 105 x 68 metros
# O terceiro terceiro começa a 70 metros da linha de gol do time próprio

# Precisamos determinar qual time Messi está atacando
# Isso requer verificar o ID do time e o período do jogo
if messi_id is not None:
    team_id = player_info[messi_id]['team_id']
    
    # Encontrar frames onde o jogador está no terceiro terceiro com a bola em jogo
    final_third_frames = []
    
    # Vamos verificar cada período, pois os times mudam de lado ao intervalo
    for period in df['period_id'].unique():
        period_df = df[df['period_id'] == period]
        
        # Determinar a direção de ataque neste período
        # Em período 1, o time próprio geralmente ataca da direita para esquerda
        # Em período 2, eles mudam de direção
        attacking_right_to_left = (period % 2 == 1 and team_id == home_team_id) or \
                                (period % 2 == 0 and team_id == away_team_id)
        
        # Definir limite de coordenada com base na direção de ataque
        if attacking_right_to_left:
            # Quando atacando da direita para esquerda, o terceiro terceiro é x < 35
            x_threshold = 35
            threshold_condition = lambda x: x < x_threshold
        else:
            # Quando atacando da esquerda para direita, o terceiro terceiro é x > 70
            x_threshold = 70
            threshold_condition = lambda x: x > x_threshold
        
        # Filtrar frames onde o jogador está no terceiro terceiro
        for idx, frame in period_df.iterrows():
            player_x_col = f"{messi_id}_x"
            
            if player_x_col in frame and not pd.isna(frame[player_x_col]):
                player_x = frame[player_x_col]
                
                if threshold_condition(player_x) and frame['ball_state'] == 'alive':
                    final_third_frames.append(idx)
    
    print(f"Encontrados {len(final_third_frames)} frames onde o jogador está no terceiro terceiro com a bola em jogo.")
    
    # Se encontrarmos momentos relevantes, exibir alguns deles
    if final_third_frames:
        print("\nVamos visualizar alguns desses momentos:")
        
        # Tomar uma amostra de frames para visualizar (os primeiros 3 momentos)
        sample_frames = final_third_frames[:min(3, len(final_third_frames))]
        
        fig, axes = plt.subplots(1, len(sample_frames), figsize=(18, 6))
        if len(sample_frames) == 1:
            axes = [axes]  # Manipular caso com apenas um frame
        
        for i, frame_idx in enumerate(sample_frames):
            frame = df.loc[frame_idx]
            timestamp = frame['timestamp']
            period = frame['period_id']
            
            # Plotar o frame
            title = f"Período {period}: {timestamp:.1f}s"
            plot_frame(frame, title=title, ax=axes[i])
            
            # Destacar o jogador que estamos focando
            player_x = frame[f"{messi_id}_x"]
            player_y = frame[f"{messi_id}_y"]
            axes[i].plot(player_x, player_y, 'yo', markersize=12, alpha=0.7)  # Yellow circle
        
        plt.tight_layout()
        plt.show()
else:
    print("Nenhum jogador selecionado para análise.")

# %% [markdown]
# ### Análise Tática de Momentos no Terceiro Terceiro
# 
# Ao analisar jogadores como Messi no terceiro terceiro, vários aspectos são importantes:
# 
# 1. **Posicionamento em relação aos defensores**: Observe como os defensores se posicionam quando nosso jogador de foco entra em áreas perigosas.
# 
# 2. **Suporte de companheiros**: Observe como companheiros se movem para fornecer opções de passe ou criar espaço.
# 
# 3. **Resposta defensiva**: Como rápida é a resposta dos defensores ao nosso jogador? Eles mantêm estrutura ou saem de posição?
# 
# 4. **Avaliação de espaço**: Olhe para momentos onde nosso jogador encontra buracos de espaço entre as linhas defensivas.
# 
# 5. **Velocidade de transição**: Observe como rapidamente a equipe se move para posições de ataque quando nosso jogador recebe a bola no terceiro terceiro.
# 
# Este tipo de análise pode revelar padrões táticos que podem não ser evidentes a partir de vídeo de jogo ou dados de evento. Os dados de rastreamento nos permitem medir relações espaciais entre jogadores e entender como atacantes como Messi manipulam defesas através de suas posições e movimentos.
# 
# Você pode adaptar esta análise para se concentrar em qualquer jogador ou situação tática específica, como:
# - Contra-ataques
# - Configurações de bola em situações de cobrança de pênalti
# - Gatilhos de pressão
# - Formação defensiva contra oponentes específicos

# %%
# Finalmente, vamos analisar o movimento do jogador em questão no terceiro terceiro
if final_third_frames and len(final_third_frames) > 5:
    # Encontrar uma sequência de frames no terceiro terceiro
    # Usaremos os primeiros 30 frames ou todos disponíveis se menos
    num_frames_to_analyze = min(30, len(final_third_frames))
    
    # Obter o índice inicial e visualizar caminhos do jogador
    start_idx = final_third_frames[0]
    
    # Focar no jogador e próximos companheiros/oponentes
    fig, ax = plot_player_paths(df, start_idx, num_frames=num_frames_to_analyze, 
                               include_ball=True)
    
    # Destacar nosso jogador de foco mais claramente
    sequence_df = df.iloc[start_idx:start_idx+num_frames_to_analyze].copy()
    
    # Obter coordenadas do jogador para cada frame, removendo valores NaN
    x_col = f"{messi_id}_x"
    y_col = f"{messi_id}_y"
    player_df = sequence_df[[x_col, y_col]].dropna()
    
    if len(player_df) >= 2:  # Precisa de pelo menos 2 pontos para desenhar um caminho
        # Obter todas as posições x e y para este jogador
        x_values = player_df[x_col].values
        y_values = player_df[y_col].values
        
        # Plotar um caminho mais visível para nosso jogador de foco
        pitch = Pitch(pitch_type='skillcorner', pitch_length=105, pitch_width=68)
        pitch.lines(x_values, y_values, lw=4, color='yellow', alpha=0.8, zorder=10, ax=ax)
        
        # Adicionar entrada de legenda para o jogador destacado
        player_name = player_info[messi_id]['name']
        jersey_no = player_info[messi_id]['jersey_no']
        ax.plot([], [], color='yellow', lw=4, label=f"{player_name} (#{jersey_no})")
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), frameon=False, ncol=3)
    
    plt.show()

# %% [markdown]
# ## Análise de Métricas Físicas dos Jogadores
#
# Uma das grandes vantagens dos dados de rastreamento é a capacidade de extrair métricas físicas precisas dos jogadores.
# Vamos calcular e analisar:
# 
# 1. Velocidade instantânea e aceleração
# 2. Distâncias percorridas (total e em diferentes zonas de intensidade)
# 3. Número e duração de sprints
# 4. Carga de trabalho físico
# 
# Estas métricas são fundamentais para preparadores físicos e cientistas esportivos avaliarem o condicionamento e fadiga dos atletas.

# %%
def calculate_player_kinematics(df, player_id, min_samples=2):
    """
    Calcula velocidade e aceleração para um jogador específico.
    
    Parâmetros:
    -----------
    df : pandas.DataFrame
        DataFrame contendo dados de rastreamento
    player_id : int
        ID do jogador para calcular métricas
    min_samples : int, padrão=2
        Número mínimo de amostras consecutivas necessárias para cálculos
    
    Retorna:
    --------
    kinematics_df : pandas.DataFrame
        DataFrame com métricas físicas calculadas
    """
    # Colunas com coordenadas do jogador
    x_col = f"{player_id}_x"
    y_col = f"{player_id}_y"
    
    # Verificar se as colunas existem no DataFrame
    if x_col not in df.columns or y_col not in df.columns:
        print(f"Dados de posição para jogador {player_id} não encontrados.")
        return None
    
    # Criar uma cópia do DataFrame com apenas as colunas necessárias
    positions_df = df[['frame_id', 'period_id', 'timestamp', x_col, y_col, 'ball_state']].copy()
    
    # Remover linhas com valores NaN nas posições do jogador
    positions_df = positions_df.dropna(subset=[x_col, y_col])
    
    # Se não houver dados suficientes, retornar None
    if len(positions_df) < min_samples:
        print(f"Dados insuficientes para jogador {player_id}.")
        return None
    
    # Ordenar por período e timestamp para garantir ordem cronológica correta
    positions_df = positions_df.sort_values(['period_id', 'timestamp'])
    
    # Calcular deslocamento em cada eixo
    positions_df['dx'] = positions_df[x_col].diff()
    positions_df['dy'] = positions_df[y_col].diff()
    
    # Calcular tempo entre frames (em segundos)
    positions_df['dt'] = positions_df['timestamp'].diff()
    
    # Marcar início de novos períodos para evitar cálculos entre períodos diferentes
    positions_df['new_period'] = positions_df['period_id'].diff() != 0
    
    # Definir dt, dx, dy como zero no início de cada período
    positions_df.loc[positions_df['new_period'], ['dt', 'dx', 'dy']] = 0
    
    # Calcular distância percorrida entre frames (em metros)
    positions_df['distance'] = np.sqrt(positions_df['dx']**2 + positions_df['dy']**2)
    
    # Calcular velocidade instantânea (m/s)
    # Evitar divisão por zero quando dt = 0
    positions_df['speed'] = np.where(
        positions_df['dt'] > 0,
        positions_df['distance'] / positions_df['dt'],
        0
    )
    
    # Converter velocidade para km/h para facilitar interpretação
    positions_df['speed_kmh'] = positions_df['speed'] * 3.6
    
    # Calcular aceleração (mudança na velocidade) (m/s²)
    positions_df['acceleration'] = positions_df['speed'].diff() / positions_df['dt']
    
    # Definir aceleração como zero no início de cada período
    positions_df.loc[positions_df['new_period'], 'acceleration'] = 0
    
    # Remover valores NaN de aceleração após cálculo de diferença
    positions_df.loc[positions_df['dt'] == 0, 'acceleration'] = 0
    
    # Adicionar coluna para identificar sprints (velocidade > 20 km/h é comum para definir sprints no futebol)
    positions_df['is_sprint'] = positions_df['speed_kmh'] > 20
    
    # Identificar início de sprints
    positions_df['sprint_start'] = (positions_df['is_sprint'] & ~positions_df['is_sprint'].shift(1).fillna(False))
    
    # Identificar final de sprints
    positions_df['sprint_end'] = (positions_df['is_sprint'] & ~positions_df['is_sprint'].shift(-1).fillna(False))
    
    # Adicionar ID do jogador para referência
    positions_df['player_id'] = player_id
    
    return positions_df

# %%
def analyze_player_performance(kinematics_df, player_info):
    """
    Analisa métricas de desempenho físico de um jogador.
    
    Parâmetros:
    -----------
    kinematics_df : pandas.DataFrame
        DataFrame com métricas de velocidade e aceleração calculadas
    player_info : dict
        Dicionário com informações do jogador
    
    Retorna:
    --------
    metrics : dict
        Dicionário com métricas de desempenho físico
    """
    # Verificar se temos dados suficientes para análise
    if kinematics_df is None or len(kinematics_df) < 10:
        return None
    
    # Extrair informações relevantes
    player_id = kinematics_df['player_id'].iloc[0]
    
    # Calcular métricas apenas quando a bola está em jogo
    in_play_df = kinematics_df[kinematics_df['ball_state'] == 'alive']
    
    # Definir zonas de intensidade (em km/h)
    # Baseado em classificações comuns na análise de futebol
    intensity_zones = {
        'parado': (0, 2),         # 0-2 km/h
        'caminhando': (2, 7),     # 2-7 km/h
        'trotando': (7, 14),      # 7-14 km/h
        'correndo': (14, 20),     # 14-20 km/h
        'sprint': (20, 100)       # >20 km/h
    }
    
    # Calcular distância total (m)
    total_distance = kinematics_df['distance'].sum()
    in_play_distance = in_play_df['distance'].sum()
    
    # Calcular distância por zona de intensidade
    distance_by_zone = {}
    time_in_zone = {}
    
    for zone, (min_speed, max_speed) in intensity_zones.items():
        # Filtrar por zona de velocidade
        zone_df = in_play_df[(in_play_df['speed_kmh'] >= min_speed) & 
                             (in_play_df['speed_kmh'] < max_speed)]
        
        # Calcular distância nesta zona
        distance_by_zone[zone] = zone_df['distance'].sum()
        
        # Calcular tempo gasto nesta zona (em segundos)
        time_in_zone[zone] = zone_df['dt'].sum()
    
    # Analisar sprints
    sprint_count = in_play_df['sprint_start'].sum()
    
    # Identificar sprints e suas durações
    sprints = []
    if sprint_count > 0:
        sprint_starts = in_play_df[in_play_df['sprint_start']].index.tolist()
        sprint_ends = in_play_df[in_play_df['sprint_end']].index.tolist()
        
        # Garantir que temos o mesmo número de inícios e fins
        min_count = min(len(sprint_starts), len(sprint_ends))
        
        for i in range(min_count):
            start_idx = sprint_starts[i]
            end_idx = sprint_ends[i]
            
            if end_idx > start_idx:  # Garantir que o fim vem após o início
                sprint_df = in_play_df.loc[start_idx:end_idx]
                
                # Calcular duração e distância do sprint
                duration = sprint_df['dt'].sum()
                distance = sprint_df['distance'].sum()
                max_speed = sprint_df['speed_kmh'].max()
                
                sprints.append({
                    'duration': duration,
                    'distance': distance,
                    'max_speed': max_speed,
                    'period_id': sprint_df['period_id'].iloc[0],
                    'timestamp_start': sprint_df['timestamp'].iloc[0]
                })
    
    # Calcular métricas resumidas
    metrics = {
        'player_id': player_id,
        'name': player_info[player_id]['name'],
        'jersey_no': player_info[player_id]['jersey_no'],
        'position': player_info[player_id]['position'],
        'team': player_info[player_id]['team_name'],
        'total_distance': total_distance,
        'in_play_distance': in_play_distance,
        'distance_by_zone': distance_by_zone,
        'time_in_zone': time_in_zone,
        'max_speed': in_play_df['speed_kmh'].max(),
        'avg_speed': in_play_df['speed_kmh'].mean(),
        'max_acceleration': in_play_df['acceleration'].max(),
        'max_deceleration': in_play_df['acceleration'].min(),
        'sprint_count': sprint_count,
        'sprints': sprints,
        'avg_sprint_distance': np.mean([s['distance'] for s in sprints]) if sprints else 0,
        'avg_sprint_duration': np.mean([s['duration'] for s in sprints]) if sprints else 0,
        'highest_speed_sprint': max([s['max_speed'] for s in sprints]) if sprints else 0,
        'high_intensity_distance': distance_by_zone.get('correndo', 0) + distance_by_zone.get('sprint', 0)
    }
    
    return metrics

# %%
def analyze_all_players(df, player_info, player_ids=None, limit_frames=None):
    """
    Analisa métricas físicas para múltiplos jogadores.
    
    Parâmetros:
    -----------
    df : pandas.DataFrame
        DataFrame contendo dados de rastreamento
    player_info : dict
        Dicionário com informações dos jogadores
    player_ids : list, opcional
        Lista de IDs de jogadores para analisar (None para todos)
    limit_frames : int, opcional
        Limitar análise aos primeiros N frames (para testes rápidos)
    
    Retorna:
    --------
    all_metrics : dict
        Dicionário com métricas para todos os jogadores
    """
    # Se nenhum jogador específico for fornecido, use todos os IDs disponíveis
    if player_ids is None:
        player_ids = home_players + away_players
    
    # Limitar frames se especificado (útil para testes)
    if limit_frames is not None:
        df_subset = df.iloc[:limit_frames].copy()
    else:
        df_subset = df
    
    # Calcular métricas para cada jogador
    all_metrics = {}
    
    for player_id in player_ids:
        print(f"Analisando jogador {player_id} ({player_info[player_id]['name']})")
        
        # Calcular velocidade e aceleração
        kinematics_df = calculate_player_kinematics(df_subset, player_id)
        
        # Analisar performance física
        if kinematics_df is not None:
            metrics = analyze_player_performance(kinematics_df, player_info)
            if metrics is not None:
                all_metrics[player_id] = metrics
    
    return all_metrics

# %%
# Vamos analisar uma sequência do jogo para todos os jogadores em campo
# Para uma demonstração mais rápida, vamos limitar a análise a um subconjunto dos dados
# Você pode remover o limite_frames para analisar toda a partida (mas levará mais tempo)

# Definir um subconjunto dos dados para análise (primeiros 3000 frames, aproximadamente 5 minutos)
limit_frames = 3000

# Analisar todos os jogadores
all_metrics = analyze_all_players(df, player_info, limit_frames=limit_frames)

print(f"Métricas físicas calculadas para {len(all_metrics)} jogadores")

# %%
# Converter métricas em um DataFrame para análise
metrics_data = []
for player_id, metrics in all_metrics.items():
    # Extrair métricas principais e adicionar à lista
    metrics_data.append({
        'player_id': player_id,
        'name': metrics['name'],
        'jersey_no': metrics['jersey_no'],
        'position': metrics['position'],
        'team': metrics['team'],
        'total_distance': metrics['total_distance'],
        'in_play_distance': metrics['in_play_distance'],
        'max_speed': metrics['max_speed'],
        'avg_speed': metrics['avg_speed'],
        'max_acceleration': metrics['max_acceleration'],
        'max_deceleration': metrics['max_deceleration'],
        'sprint_count': metrics['sprint_count'],
        'high_intensity_distance': metrics['high_intensity_distance'],
        'distance_sprint': metrics['distance_by_zone'].get('sprint', 0),
        'distance_running': metrics['distance_by_zone'].get('correndo', 0),
        'distance_jogging': metrics['distance_by_zone'].get('trotando', 0),
        'distance_walking': metrics['distance_by_zone'].get('caminhando', 0)
    })

# Criar DataFrame
metrics_df = pd.DataFrame(metrics_data)

# Exibir as principais métricas
print("Métricas físicas por jogador:")
display(metrics_df[['name', 'position', 'team', 'total_distance', 'max_speed', 'sprint_count']])

# %%
# Visualizar métricas físicas por posição
def plot_metrics_by_position(metrics_df):
    """
    Visualiza métricas físicas agrupadas por posição dos jogadores.
    
    Parâmetros:
    -----------
    metrics_df : pandas.DataFrame
        DataFrame com métricas físicas calculadas
    """
    # Agrupar por posição
    position_metrics = metrics_df.groupby('position').agg({
        'total_distance': 'mean',
        'max_speed': 'mean',
        'sprint_count': 'mean',
        'high_intensity_distance': 'mean'
    }).reset_index()
    
    # Criar visualização com subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Distância total por posição
    axes[0, 0].bar(position_metrics['position'], position_metrics['total_distance'], color='skyblue')
    axes[0, 0].set_title('Distância Média Total por Posição (m)')
    axes[0, 0].set_ylabel('Distância (m)')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Velocidade máxima por posição
    axes[0, 1].bar(position_metrics['position'], position_metrics['max_speed'], color='lightgreen')
    axes[0, 1].set_title('Velocidade Máxima Média por Posição (km/h)')
    axes[0, 1].set_ylabel('Velocidade (km/h)')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Número de sprints por posição
    axes[1, 0].bar(position_metrics['position'], position_metrics['sprint_count'], color='salmon')
    axes[1, 0].set_title('Número Médio de Sprints por Posição')
    axes[1, 0].set_ylabel('Número de Sprints')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Distância em alta intensidade por posição
    axes[1, 1].bar(position_metrics['position'], position_metrics['high_intensity_distance'], color='purple')
    axes[1, 1].set_title('Distância Média em Alta Intensidade por Posição (m)')
    axes[1, 1].set_ylabel('Distância (m)')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.show()

# Visualizar métricas por posição
plot_metrics_by_position(metrics_df)

# %%
# Visualizar perfil de intensidade por jogador
def plot_player_intensity_profile(metrics_df, num_players=5):
    """
    Visualiza o perfil de intensidade para os jogadores com maior distância total.
    
    Parâmetros:
    -----------
    metrics_df : pandas.DataFrame
        DataFrame com métricas físicas calculadas
    num_players : int, padrão=5
        Número de jogadores para visualizar
    """
    # Selecionar os jogadores com maior distância total
    top_players = metrics_df.nlargest(num_players, 'total_distance')
    
    # Criar visualização
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Definir largura das barras
    bar_width = 0.6 / num_players
    positions = np.arange(4)  # 4 zonas de intensidade
    
    # Cores para zonas de intensidade
    colors = ['steelblue', 'lightseagreen', 'orange', 'firebrick']
    
    # Plotar barras para cada jogador
    for i, (idx, player) in enumerate(top_players.iterrows()):
        # Extrair dados de distância por zona
        distances = [
            player['distance_walking'],
            player['distance_jogging'],
            player['distance_running'],
            player['distance_sprint']
        ]
        
        # Calcular posições das barras
        bar_positions = positions + (i - num_players/2 + 0.5) * bar_width
        
        # Plotar barras
        bars = ax.bar(bar_positions, distances, width=bar_width, 
                      label=f"{player['name']} (#{player['jersey_no']})")
    
    # Configurar eixos e legendas
    ax.set_xticks(positions)
    ax.set_xticklabels(['Caminhando', 'Trotando', 'Correndo', 'Sprint'])
    ax.set_ylabel('Distância (m)')
    ax.set_title('Perfil de Intensidade por Jogador')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.show()

# Visualizar perfil de intensidade para os 5 jogadores com maior distância
plot_player_intensity_profile(metrics_df, num_players=5)

# %%
# Analisar sprint específico de um jogador para demonstração
def analyze_single_sprint(df, player_id, sprint_info, player_info):
    """
    Analisa e visualiza um sprint específico de um jogador.
    
    Parâmetros:
    -----------
    df : pandas.DataFrame
        DataFrame contendo dados de rastreamento
    player_id : int
        ID do jogador para analisar sprint
    sprint_info : dict
        Dicionário com informações do sprint (período, timestamp)
    player_info : dict
        Dicionário com informações do jogador
    """
    # Extrair informações do sprint
    period_id = sprint_info['period_id']
    timestamp_start = sprint_info['timestamp_start']
    
    # Filtrar dados próximos ao sprint
    buffer = 3  # segundos antes/depois do sprint
    sprint_sequence = df[(df['period_id'] == period_id) & 
                         (df['timestamp'] >= timestamp_start - buffer) &
                         (df['timestamp'] <= timestamp_start + buffer + sprint_info['duration'])]
    
    # Se não houver dados suficientes, sair
    if len(sprint_sequence) < 5:
        print(f"Dados insuficientes para analisar este sprint.")
        return
    
    # Calcular velocidade e aceleração para esta sequência
    kinematics_df = calculate_player_kinematics(sprint_sequence, player_id)
    
    if kinematics_df is None:
        print(f"Não foi possível calcular cinemática para este sprint.")
        return
    
    # Criar visualização
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Plotar velocidade
    ax1.plot(kinematics_df['timestamp'], kinematics_df['speed_kmh'], 'b-', linewidth=2)
    ax1.axhline(y=20, color='r', linestyle='--', alpha=0.7, label='Limiar de Sprint (20 km/h)')
    ax1.set_ylabel('Velocidade (km/h)')
    ax1.set_title(f"Sprint de {player_info[player_id]['name']} - Duração: {sprint_info['duration']:.1f}s, Distância: {sprint_info['distance']:.1f}m")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Plotar aceleração
    ax2.plot(kinematics_df['timestamp'], kinematics_df['acceleration'], 'g-', linewidth=2)
    ax2.axhline(y=0, color='k', linestyle='-', alpha=0.2)
    ax2.set_xlabel('Tempo (s)')
    ax2.set_ylabel('Aceleração (m/s²)')
    ax2.grid(True, alpha=0.3)
    
    # Destacar região do sprint
    sprint_start = timestamp_start
    sprint_end = timestamp_start + sprint_info['duration']
    
    # Adicionar área sombreada para o período do sprint
    ax1.axvspan(sprint_start, sprint_end, alpha=0.2, color='yellow', label='Duração do Sprint')
    ax2.axvspan(sprint_start, sprint_end, alpha=0.2, color='yellow')
    
    plt.tight_layout()
    plt.show()

# Selecionar um jogador com sprints para análise
sprint_players = [pid for pid, metrics in all_metrics.items() if metrics['sprint_count'] > 0]

if sprint_players:
    # Escolher o primeiro jogador com sprints
    example_player_id = sprint_players[0]
    player_sprints = all_metrics[example_player_id]['sprints']
    
    if player_sprints:
        # Escolher o sprint mais longo para análise
        longest_sprint = max(player_sprints, key=lambda x: x['distance'])
        
        print(f"Analisando sprint de {player_info[example_player_id]['name']}:")
        print(f"  Duração: {longest_sprint['duration']:.2f}s")
        print(f"  Distância: {longest_sprint['distance']:.2f}m")
        print(f"  Velocidade máxima: {longest_sprint['max_speed']:.2f} km/h")
        
        # Analisar o sprint
        analyze_single_sprint(df, example_player_id, longest_sprint, player_info)
else:
    print("Nenhum jogador com sprints encontrado na amostra analisada.")

# %% [markdown]
# ## Interpretação das Métricas Físicas
# 
# A análise de métricas físicas fornece insights valiosos para:
# 
# 1. **Preparadores Físicos**:
#    - Monitorar carga de trabalho durante jogos e treinos
#    - Identificar jogadores em risco de fadiga ou lesão
#    - Personalizar programas de condicionamento baseados em demandas específicas de posição
# 
# 2. **Treinadores Táticos**:
#    - Entender como o esforço físico se relaciona com o sistema tático
#    - Avaliar se jogadores estão atingindo zonas de campo exigidas pela estratégia
#    - Planejar substituições baseadas em dados de fadiga
# 
# 3. **Analistas de Desempenho**:
#    - Comparar métricas físicas entre jogos e temporadas
#    - Identificar tendências de condicionamento ao longo do tempo
#    - Estabelecer benchmarks por posição e estilo de jogo
# 
# As métricas mais relevantes incluem:
# 
# - **Distância total**: Indicador básico de volume de trabalho
# - **Distância em alta intensidade**: Mais correlacionada com demandas do futebol moderno
# - **Perfil de intensidade**: Distribuição de esforço em diferentes zonas de velocidade
# - **Número e qualidade de sprints**: Crucial para momentos decisivos do jogo
# - **Aceleração/desaceleração**: Grande impacto metabólico e neuromuscular 