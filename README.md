# Visualização de Dados de Rastreamento de Futebol

Este repositório contém utilitários e exemplos para visualizar dados de rastreamento de futebol usando os pacotes kloppy e mplsoccer. O foco está nos dados de rastreamento do PFF FC da Copa do Mundo FIFA 2022 masculina.

## Instruções de Configuração

### 1. Clonar o Repositório

```bash
git clone https://github.com/seunome/football-tracking-viz.git
cd football-tracking-viz
```

### 2. Criar um Ambiente Virtual

```bash
# Criar um ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
# Para Windows:
venv\Scripts\activate
# Para macOS/Linux:
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configuração Automatizada

Para sua conveniência, incluímos scripts de configuração automatizada:

- **Linux/macOS**: Execute `./setup_venv.sh`
- **Windows**: Execute `setup_venv.bat`

Estes scripts criarão um ambiente virtual, instalarão as dependências e baixarão dados de exemplo.

## Dados

Este projeto utiliza dados de rastreamento do PFF FC da Copa do Mundo FIFA 2022 masculina. Os conjuntos de dados podem ser solicitados através [deste link](https://www.blog.fc.pff.com/blog/pff-fc-release-2022-world-cup-data).

Os principais componentes dos dados incluem:
- **Dados de Rastreamento**: Contém posições dos jogadores e da bola, armazenados separadamente por jogo como `{game_id}.jsonl.bz2`
- **Dados de Eventos**: Contém eventos das partidas para todos os jogos armazenados em um único arquivo: `events.json`
- **Metadados**: Contém informações do jogo (times, data, etc.) armazenados como `{game_id}.json`
- **Elencos**: Contém informações das escalações armazenadas como `{game_id}.json`

Você pode baixar dados de exemplo para teste executando:

```bash
python download_sample_data.py
```

## Notebooks e Scripts

Este repositório contém tanto notebooks Jupyter quanto scripts Python para visualização:

### Scripts Python (com jupytext)

Utilizamos [jupytext](https://jupytext.readthedocs.io/) para armazenar notebooks como scripts Python amigáveis ao controle de versão:

- `pff.py`: Carregamento básico dos dados de rastreamento PFF
- `tracking_visualization.py`: Exemplos abrangentes de visualização incluindo frames e animações

Estes arquivos `.py` podem ser utilizados de duas formas:

1. **Abrir diretamente como notebooks no JupyterLab/Jupyter Notebook**:  
   Se você tiver o jupytext instalado, estes scripts Python abrirão automaticamente como notebooks.

2. **Converter para formato .ipynb**:  
   ```bash
   jupytext --to notebook pff.py
   jupytext --to notebook tracking_visualization.py
   ```

3. **Sincronizar alterações entre .py e .ipynb**:  
   ```bash
   jupytext --sync tracking_visualization.ipynb  # Sincroniza com tracking_visualization.py
   ```

### Exemplos

Os scripts/notebooks incluem exemplos de:
- Carregamento e processamento de dados de rastreamento usando kloppy
- Visualização de frames individuais de situações de jogo
- Criação de animações de movimentos dos jogadores
- Exportação de visualizações como GIFs, vídeos MP4 ou HTML interativo

## Licença

Este repositório está licenciado sob a Licença MIT - consulte o arquivo LICENSE para detalhes. 