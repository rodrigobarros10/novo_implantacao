"""
Aplicação principal do Sistema ETL com Streamlit.

Interface web para gerenciamento de conexões, jobs e execuções do ETL.
"""

import streamlit as st
from pathlib import Path
import sys

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.base import init_db
from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)

# Configurar página Streamlit
st.set_page_config(
    page_title="Sistema ETL - Supermercados",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar banco de dados
@st.cache_resource
def init_database():
    """Inicializa conexão com banco de dados de metadados."""
    settings = get_settings()
    return init_db(settings.DATABASE_URL)


# Inicializar
try:
    db_engine = init_database()
except Exception as e:
    st.error(f"Erro ao conectar ao banco de dados: {str(e)}")
    st.stop()

# Estilos customizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-text {
        color: #00cc00;
        font-weight: bold;
    }
    .error-text {
        color: #cc0000;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🏪 Sistema ETL")
    st.write("Supermercados")
    st.divider()
    
    menu = st.radio(
        "Navegação",
        options=[
            "📊 Home",
            "🔌 Conexões",
            "💼 Jobs",
            "⚙️ Execuções",
            "📈 Monitoramento"
        ],
        help="Selecione uma seção da aplicação"
    )

# Páginas
if menu == "📊 Home":
    from ui.pages.home import render_home
    render_home()

elif menu == "🔌 Conexões":
    from ui.pages.connections import render_connections
    render_connections()

elif menu == "💼 Jobs":
    from ui.pages.jobs import render_jobs
    render_jobs()

elif menu == "⚙️ Execuções":
    from ui.pages.execucoes import render_execucoes
    render_execucoes()

elif menu == "📈 Monitoramento":
    from ui.pages.monitoramento import render_monitoramento
    render_monitoramento()

# Footer
st.divider()
st.caption("Sistema ETL para Supermercados v1.0 | © 2024")