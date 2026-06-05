"""
Página Home - Dashboard principal do sistema.
"""

import streamlit as st
from db.base import get_session
from db.models.connections import ConnectionModel, JobModel, ExecutionModel
from utils.logger import get_logger

logger = get_logger(__name__)


def render_home():
    """Renderiza a página inicial/dashboard."""
    
    st.markdown("<h1 class='main-header'>📊 Dashboard</h1>", unsafe_allow_html=True)
    st.write("Bem-vindo ao Sistema ETL para Supermercados!")
    
    # Estatísticas
    session = get_session()
    
    try:
        num_connections = session.query(ConnectionModel).filter(
            ConnectionModel.is_active == True
        ).count()
        
        num_jobs = session.query(JobModel).filter(
            JobModel.is_active == True
        ).count()
        
        recent_executions = session.query(ExecutionModel).order_by(
            ExecutionModel.start_time.desc()
        ).limit(10).all()
        
        # Cards de métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🔌 Conexões",
                num_connections,
                help="Total de conexões cadastradas"
            )
        
        with col2:
            st.metric(
                "💼 Jobs",
                num_jobs,
                help="Total de jobs ETL cadastrados"
            )
        
        with col3:
            total_rows = sum(e.rows_loaded for e in recent_executions)
            st.metric(
                "📈 Linhas Carregadas",
                f"{total_rows:,}",
                help="Total de linhas carregadas nas últimas execuções"
            )
        
        with col4:
            success_count = sum(1 for e in recent_executions if e.status == 'SUCCESS')
            st.metric(
                "✅ Execuções OK",
                success_count,
                help="Execuções bem-sucedidas recentemente"
            )
        
        # Últimas execuções
        st.divider()
        st.subheader("⚙️ Últimas Execuções")
        
        if recent_executions:
            execution_data = []
            for exec_model in recent_executions[:5]:
                execution_data.append({
                    'Job ID': exec_model.job_id,
                    'Status': '✅ SUCCESS' if exec_model.status == 'SUCCESS' else '❌ FAILED',
                    'Linhas': exec_model.rows_loaded,
                    'Início': exec_model.start_time.strftime('%d/%m/%Y %H:%M:%S'),
                    'Duração': f"{exec_model.duration_seconds}s" if exec_model.duration_seconds else '-'
                })
            
            import pandas as pd
            df = pd.DataFrame(execution_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma execução realizada ainda.")
        
        # Dicas
        st.divider()
        st.subheader("💡 Dicas de Uso")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🔌 Conexões**
            - Cadastre conexões de origem e destino na aba "Conexões"
            - Sempre teste a conexão antes de usar em um job
            - Use nomes descritivos para facilitar identificação
            """)
        
        with col2:
            st.markdown("""
            **💼 Jobs**
            - Crie jobs que definem qual entidade será processada
            - Configure transformações e validações específicas
            - Agende execuções periódicas com Cron
            """)
    
    finally:
        session.close()
