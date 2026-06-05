"""
Página de Conexões - Interface para gerenciar conexões com bancos de dados.

Permite criar, editar, testar e deletar conexões de origem e destino.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from core.connections.factory import ConnectionFactory, _register_default_drivers
from core.connections.base import ConnectionConfig
from db.models.connections import ConnectionModel
from db.base import get_session
from utils.logger import get_logger
from utils.exceptions import ConnectionException, ConnectionTestFailedError

logger = get_logger(__name__)

# Registrar drivers
_register_default_drivers()


def render_connections():
    """Renderiza a página de gestão de conexões."""
    
    st.markdown("<h1 class='main-header'>🔌 Gestão de Conexões</h1>", unsafe_allow_html=True)
    st.write("Cadastre, edite e teste conexões com bancos de dados de origem e destino.")
    
    # Abas
    tab1, tab2, tab3 = st.tabs(["📋 Listar Conexões", "➕ Nova Conexão", "✏️ Editar Conexão"])
    
    # ABA 1: Listar Conexões
    with tab1:
        st.subheader("Conexões Cadastradas")
        list_connections()
    
    # ABA 2: Nova Conexão
    with tab2:
        st.subheader("Cadastrar Nova Conexão")
        create_connection_form()
    
    # ABA 3: Editar Conexão
    with tab3:
        st.subheader("Editar Conexão")
        edit_connection_form()


def list_connections():
    """Lista todas as conexões cadastradas."""
    session = get_session()
    
    try:
        connections = session.query(ConnectionModel).filter(
            ConnectionModel.is_active == True
        ).all()
        
        if not connections:
            st.info("Nenhuma conexão cadastrada ainda. Crie uma nova na aba 'Nova Conexão'.")
            return
        
        # Criar DataFrame para exibição
        data = []
        for conn in connections:
            data.append({
                'ID': conn.id,
                'Nome': conn.name,
                'Tipo': conn.connection_type.upper(),
                'Host': conn.host,
                'Porta': conn.port,
                'Banco': conn.database,
                'Status': '✅ Válida' if conn.is_valid else '❌ Não testada',
                'Teste': f"{conn.tested_at.strftime('%d/%m/%Y %H:%M') if conn.tested_at else 'Nunca'}",
                'Ação': conn.id
            })
        
        df = pd.DataFrame(data)
        
        # Remover coluna de ação do DataFrame para exibição
        display_df = df.drop('Ação', axis=1)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Botões de ação
        st.divider()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Testar Conexões"):
                test_all_connections(connections)
        
        with col2:
            selected_id = st.selectbox(
                "Selecione uma conexão para testar",
                options=[c.id for c in connections],
                format_func=lambda x: next(c.name for c in connections if c.id == x),
                key="test_select"
            )
            if st.button("🧪 Testar Selecionada"):
                test_single_connection(selected_id)
        
        with col3:
            delete_id = st.selectbox(
                "Selecione uma conexão para deletar",
                options=[c.id for c in connections],
                format_func=lambda x: next(c.name for c in connections if c.id == x),
                key="delete_select"
            )
            if st.button("🗑️ Deletar"):
                delete_connection(delete_id)
    
    finally:
        session.close()


def create_connection_form():
    """Formulário para criar nova conexão."""
    
    # Drivers disponíveis
    drivers = ConnectionFactory.get_supported_drivers()
    
    with st.form("new_connection_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Nome da Conexão",
                help="Identificador único para esta conexão",
                placeholder="minha_conexao_mysql"
            )
            
            conn_type = st.selectbox(
                "Tipo de Banco de Dados",
                options=drivers,
                help="Selecione o tipo de banco de dados",
                format_func=lambda x: x.upper()
            )
            
            host = st.text_input(
                "Host",
                help="Hostname ou endereço IP do servidor",
                placeholder="localhost"
            )
            
            port = st.number_input(
                "Porta",
                min_value=1,
                max_value=65535,
                value=5432,
                help="Porta de conexão do banco de dados"
            )
        
        with col2:
            database = st.text_input(
                "Nome do Banco de Dados",
                help="Nome do banco de dados a conectar",
                placeholder="meu_banco"
            )
            
            username = st.text_input(
                "Usuário",
                help="Usuário de autenticação",
                placeholder="admin"
            )
            
            password = st.text_input(
                "Senha",
                type="password",
                help="Senha de autenticação (criptografada)",
                placeholder="••••••••"
            )
            
            timeout = st.number_input(
                "Timeout (segundos)",
                min_value=1,
                max_value=300,
                value=30,
                help="Tempo máximo para estabelecer conexão"
            )
        
        # Parâmetros adicionais
        st.divider()
        st.write("**Parâmetros Avançados (opcional)**")
        
        col3, col4 = st.columns(2)
        
        with col3:
            pool_size = st.number_input(
                "Tamanho do Pool",
                min_value=1,
                max_value=50,
                value=5,
                help="Número de conexões mantidas em cache"
            )
        
        with col4:
            ssl_mode = st.selectbox(
                "Modo SSL",
                options=["disable", "allow", "prefer", "require"],
                help="Modo SSL para conexão (PostgreSQL)",
                index=0
            )
        
        # Botão de submit
        submitted = st.form_submit_button("✅ Criar Conexão", use_container_width=True)
        
        if submitted:
            if not all([name, host, database, username, password]):
                st.error("❌ Preencha todos os campos obrigatórios!")
            else:
                create_new_connection(
                    name=name,
                    conn_type=conn_type,
                    host=host,
                    port=int(port),
                    database=database,
                    username=username,
                    password=password,
                    timeout=int(timeout),
                    pool_size=int(pool_size),
                    ssl_mode=ssl_mode
                )


def create_new_connection(name: str, conn_type: str, host: str, port: int,
                         database: str, username: str, password: str,
                         timeout: int, pool_size: int, ssl_mode: str):
    """Cria nova conexão e a salva no banco."""
    
    session = get_session()
    
    try:
        # Verificar se já existe
        existing = session.query(ConnectionModel).filter(
            ConnectionModel.name == name
        ).first()
        
        if existing:
            st.error(f"❌ Conexão com nome '{name}' já existe!")
            return
        
        # Criar configuração
        config = ConnectionConfig(
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
            connection_type=conn_type,
            timeout=timeout,
            pool_size=pool_size,
            extra_params={"ssl_mode": ssl_mode} if conn_type == "postgresql" else None
        )
        
        # Testar conexão
        with st.spinner("🧪 Testando conexão..."):
            try:
                connection = ConnectionFactory.create_connection(config)
                connection.test_connection()
                is_valid = True
                error_msg = None
            except Exception as e:
                is_valid = False
                error_msg = str(e)
                logger.error(f"Falha ao testar conexão: {error_msg}")
        
        # Salvar no banco
        from cryptography.fernet import Fernet
        import os
        
        # Criptografar senha
        key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
        cipher = Fernet(key)
        encrypted_password = cipher.encrypt(password.encode())
        
        conn_model = ConnectionModel(
            name=name,
            connection_type=conn_type,
            host=host,
            port=port,
            database=database,
            username=username,
            password=encrypted_password,
            timeout=timeout,
            pool_size=pool_size,
            extra_params={"ssl_mode": ssl_mode} if conn_type == "postgresql" else None,
            is_valid=is_valid,
            tested_at=datetime.utcnow() if is_valid else None,
            last_error=error_msg
        )
        
        session.add(conn_model)
        session.commit()
        
        if is_valid:
            st.success(f"✅ Conexão '{name}' criada e validada com sucesso!")
            logger.info(f"Nova conexão criada: {name}")
        else:
            st.warning(f"⚠️ Conexão '{name}' criada, mas falha no teste: {error_msg}")
            logger.warning(f"Conexão criada com falha no teste: {name}")
    
    except Exception as e:
        st.error(f"❌ Erro ao criar conexão: {str(e)}")
        logger.error(f"Erro ao criar conexão: {str(e)}")
    
    finally:
        session.close()


def test_single_connection(connection_id: int):
    """Testa uma conexão específica."""
    session = get_session()
    
    try:
        conn_model = session.query(ConnectionModel).filter(
            ConnectionModel.id == connection_id
        ).first()
        
        if not conn_model:
            st.error("Conexão não encontrada")
            return
        
        # Descriptografar senha
        from cryptography.fernet import Fernet
        import os
        
        key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
        cipher = Fernet(key)
        decrypted_password = cipher.decrypt(conn_model.password).decode()
        
        # Criar config
        config = ConnectionConfig(
            host=conn_model.host,
            port=conn_model.port,
            database=conn_model.database,
            username=conn_model.username,
            password=decrypted_password,
            connection_type=conn_model.connection_type,
            timeout=conn_model.timeout,
            pool_size=conn_model.pool_size,
            extra_params=conn_model.extra_params
        )
        
        with st.spinner(f"🧪 Testando '{conn_model.name}'..."):
            try:
                connection = ConnectionFactory.create_connection(config)
                connection.test_connection()
                
                # Atualizar no banco
                conn_model.is_valid = True
                conn_model.tested_at = datetime.utcnow()
                conn_model.last_error = None
                session.commit()
                
                st.success(f"✅ Teste bem-sucedido para '{conn_model.name}'!")
                logger.info(f"Teste bem-sucedido: {conn_model.name}")
            except Exception as e:
                error_msg = str(e)
                conn_model.is_valid = False
                conn_model.last_error = error_msg
                session.commit()
                
                st.error(f"❌ Teste falhou: {error_msg}")
                logger.error(f"Teste falhou para {conn_model.name}: {error_msg}")
    
    finally:
        session.close()


def test_all_connections(connections: list):
    """Testa todas as conexões."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, conn in enumerate(connections):
        status_text.text(f"Testando {conn.name}... ({i+1}/{len(connections)})")
        test_single_connection(conn.id)
        progress_bar.progress((i + 1) / len(connections))
    
    status_text.text("✅ Teste concluído!")


def edit_connection_form():
    """Formulário para editar uma conexão existente."""
    session = get_session()
    
    try:
        connections = session.query(ConnectionModel).filter(
            ConnectionModel.is_active == True
        ).all()
        
        if not connections:
            st.info("Nenhuma conexão disponível para editar.")
            return
        
        selected_conn = st.selectbox(
            "Selecione uma conexão para editar",
            options=connections,
            format_func=lambda x: f"{x.name} ({x.connection_type.upper()})"
        )
        
        st.info("🔒 Por razões de segurança, a senha não pode ser editada. "
                "Crie uma nova conexão com senha diferente se necessário.")
        
        with st.form("edit_connection_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_host = st.text_input(
                    "Host",
                    value=selected_conn.host
                )
                new_port = st.number_input(
                    "Porta",
                    value=selected_conn.port,
                    min_value=1,
                    max_value=65535
                )
            
            with col2:
                new_database = st.text_input(
                    "Banco de Dados",
                    value=selected_conn.database
                )
                new_timeout = st.number_input(
                    "Timeout (segundos)",
                    value=selected_conn.timeout,
                    min_value=1
                )
            
            submitted = st.form_submit_button("✅ Atualizar Conexão")
            
            if submitted:
                selected_conn.host = new_host
                selected_conn.port = new_port
                selected_conn.database = new_database
                selected_conn.timeout = new_timeout
                selected_conn.updated_at = datetime.utcnow()
                session.commit()
                
                st.success(f"✅ Conexão '{selected_conn.name}' atualizada!")
                logger.info(f"Conexão atualizada: {selected_conn.name}")
    
    finally:
        session.close()


def delete_connection(connection_id: int):
    """Deleta uma conexão (soft delete)."""
    session = get_session()
    
    try:
        conn_model = session.query(ConnectionModel).filter(
            ConnectionModel.id == connection_id
        ).first()
        
        if conn_model:
            conn_model.is_active = False
            session.commit()
            st.success(f"✅ Conexão '{conn_model.name}' deletada!")
            logger.info(f"Conexão deletada: {conn_model.name}")
        else:
            st.error("Conexão não encontrada")
    
    except Exception as e:
        st.error(f"❌ Erro ao deletar: {str(e)}")
    
    finally:
        session.close()