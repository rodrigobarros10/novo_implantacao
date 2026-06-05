"""
Factory Pattern para criar conexões de banco de dados.

Permite instanciar dinamicamente diferentes tipos de conexões
sem acoplamento direto às implementações específicas.
"""

from typing import Dict, Type
from core.connections.base import DatabaseConnection, ConnectionConfig
from utils.logger import get_logger
from utils.exceptions import EngineNotSupportedError

logger = get_logger(__name__)


class ConnectionFactory:
    """
    Factory para criar instâncias de conexões de banco de dados.
    
    Mantém um registro de drivers suportados e fornece um método
    centralizado para instanciar conexões.
    """
    
    # Registro de drivers suportados
    _drivers: Dict[str, Type[DatabaseConnection]] = {}
    
    @classmethod
    def register_driver(cls, driver_type: str, 
                       driver_class: Type[DatabaseConnection]) -> None:
        """
        Registra um novo driver de banco de dados.
        
        Args:
            driver_type: Identificador do driver (ex: 'mysql', 'postgresql')
            driver_class: Classe que implementa DatabaseConnection
        """
        if not issubclass(driver_class, DatabaseConnection):
            raise TypeError(f"{driver_class} deve herdar de DatabaseConnection")
        
        cls._drivers[driver_type.lower()] = driver_class
        logger.info(f"Driver '{driver_type}' registrado com sucesso")
    
    @classmethod
    def create_connection(cls, config: ConnectionConfig) -> DatabaseConnection:
        """
        Cria uma instância de conexão baseado no tipo configurado.
        
        Args:
            config: Configuração de conexão
        
        Returns:
            Instância de DatabaseConnection apropriada
        
        Raises:
            EngineNotSupportedError: Se o tipo de driver não é suportado
        """
        driver_type = config.connection_type.lower()
        
        if driver_type not in cls._drivers:
            available = ', '.join(cls._drivers.keys())
            raise EngineNotSupportedError(
                f"Driver '{driver_type}' não suportado. "
                f"Disponíveis: {available}"
            )
        
        driver_class = cls._drivers[driver_type]
        logger.info(f"Criando conexão do tipo '{driver_type}'")
        
        return driver_class(config)
    
    @classmethod
    def get_supported_drivers(cls) -> list:
        """
        Retorna lista de drivers suportados.
        
        Returns:
            Lista com nomes dos drivers disponíveis
        """
        return sorted(list(cls._drivers.keys()))
    
    @classmethod
    def is_driver_supported(cls, driver_type: str) -> bool:
        """
        Verifica se um driver é suportado.
        
        Args:
            driver_type: Tipo de driver a verificar
        
        Returns:
            True se suportado, False caso contrário
        """
        return driver_type.lower() in cls._drivers


# Registrar drivers default
def _register_default_drivers():
    """Registra os drivers padrão do sistema."""
    from core.connections.postgresql import PostgreSQLConnection
    from core.connections.mysql import MySQLConnection
    from core.connections.mssql import MSSQLConnection
    from core.connections.oracle import OracleConnection
    
    ConnectionFactory.register_driver('postgresql', PostgreSQLConnection)
    ConnectionFactory.register_driver('mysql', MySQLConnection)
    ConnectionFactory.register_driver('mssql', MSSQLConnection)
    ConnectionFactory.register_driver('oracle', OracleConnection)
