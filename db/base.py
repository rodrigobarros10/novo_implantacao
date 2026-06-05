"""
Configuração do banco de dados PostgreSQL para metadados.

Configura SQLAlchemy para persistência de configurações do sistema.
"""

from sqlalchemy import create_engine, Engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# Base para modelos SQLAlchemy
Base = declarative_base()

# Variável global para a engine
_engine: Optional[Engine] = None


def init_db(database_url: str) -> Engine:
    """
    Inicializa a conexão com PostgreSQL.
    
    Args:
        database_url: URL de conexão (ex: postgresql://user:pass@localhost/dbname)
    
    Returns:
        Engine do SQLAlchemy
    """
    global _engine
    
    try:
        logger.info(f"Inicializando banco de dados: {database_url}")
        
        _engine = create_engine(
            database_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verifica conexões antes de usar
            pool_recycle=3600     # Recicla conexões a cada hora
        )
        
        # Testar conexão
        # Testar conexão
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("Conexão com banco de dados estabelecida com sucesso")
        
        # IMPORTANTE: Importar os modelos aqui para o SQLAlchemy saber que eles existem
        import db.models.connections
        
        # Criar tabelas
        Base.metadata.create_all(_engine)
        logger.info("Tabelas criadas/verificadas com sucesso")
        
        return _engine
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
        raise


def get_engine() -> Engine:
    """
    Retorna a engine global.
    
    Returns:
        Engine do SQLAlchemy
    
    Raises:
        RuntimeError: Se banco não foi inicializado
    """
    if _engine is None:
        raise RuntimeError(
            "Banco de dados não inicializado. Chamar init_db() primeiro."
        )
    return _engine


def get_session():
    """
    Factory para criar novas sessões.
    
    Returns:
        Sessão do SQLAlchemy
    """
    if _engine is None:
        raise RuntimeError(
            "Banco de dados não inicializado. Chamar init_db() primeiro."
        )
    
    SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    return SessionLocal()