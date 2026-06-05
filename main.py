"""
Arquivo principal para executar o Sistema ETL.

Execute com: streamlit run main.py
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

# Importar e executar a aplicação Streamlit
from ui.app import *
