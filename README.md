# Dados de Rastreamento de Futebol

Este repositório contém utilitários e exemplos para visualizar dados de rastreamento de futebol usando os pacotes kloppy e mplsoccer. O foco está nos dados de rastreamento do PFF FC da Copa do Mundo FIFA 2022 masculina.

## Instruções de Configuração

### 1. Clonar o Repositório

```bash
git clone https://github.com/seunome/aula_tracking_footure.git
cd aula_tracking_footure
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
- **Metadados**: Contém informações do jogo (times, data, etc.) armazenados como `{game_id}.json`
- **Elencos**: Contém informações das escalações armazenadas como `{game_id}.json`

Você pode baixar dados de exemplo para teste executando o comando abaixo, mas eles já se encontram no repositório.

```bash
python download_sample_data.py
```
