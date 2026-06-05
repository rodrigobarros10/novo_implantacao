"""
Configurações da aplicação.

Gerencia variáveis de ambiente e configurações globais do sistema.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # Database (Metadados)
    DATABASE_URL: str = "postgresql://etl_user:etl_password@localhost:5432/etl_metadata"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # PySpark
    SPARK_MASTER: str = "local[*]"
    SPARK_MEMORY: str = "2g"
    SPARK_PARTITIONS: int = 200
    
    # Timeouts
    CONNECTION_TIMEOUT: int = 30
    QUERY_TIMEOUT: int = 3600
    
    # Criptografia
    ENCRYPTION_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Retorna instância singleton das configurações."""
    global _settings
    
    if _settings is None:
        _settings = Settings()
    
    return _settings
