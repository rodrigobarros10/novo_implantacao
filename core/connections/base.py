"""
Interface abstrata para conexões com banco de dados.

Define o contrato que toda implementação de conexão deve seguir,
permitindo a extensão com novos tipos de banco de dados.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ConnectionConfig:
    """
    Configuração genérica de conexão.
    
    Attributes:
        host: Hostname ou IP do banco de dados
        port: Porta de conexão
        database: Nome do banco de dados
        username: Usuário de autenticação
        password: Senha de autenticação
        connection_type: Tipo de banco (mysql, postgresql, mssql, oracle)
        timeout: Timeout de conexão em segundos
        pool_size: Tamanho do pool de conexões
        extra_params: Parâmetros adicionais específicos do driver
    """
    host: str
    port: int
    database: str
    username: str
    password: str
    connection_type: str
    timeout: int = 30
    pool_size: int = 5
    extra_params: Optional[Dict[str, Any]] = None


class DatabaseConnection(ABC):
    """
    Classe abstrata que define a interface para conexões com banco de dados.
    
    Todas as implementações específicas (MySQL, PostgreSQL, etc) devem
    herdar desta classe e implementar os métodos abstratos.
    """
    
    def __init__(self, config: ConnectionConfig):
        """
        Inicializa a conexão.
        
        Args:
            config: Configuração de conexão
        """
        self.config = config
        self._connection = None
        self._is_connected = False
        logger.info(f"Inicializando conexão {self.config.connection_type} "
                   f"com {self.config.host}:{self.config.port}")
    
    @abstractmethod
    def connect(self) -> bool:
        """
        Estabelece conexão com o banco de dados.
        
        Returns:
            True se conexão estabelecida com sucesso, False caso contrário
        
        Raises:
            ConnectionException: Se ocorrer erro na conexão
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """
        Encerra a conexão com o banco de dados.
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Testa se a conexão está ativa e funcional.
        
        Returns:
            True se a conexão está ok, False caso contrário
        """
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """
        Executa uma query SELECT e retorna os resultados.
        
        Args:
            query: Query SQL a executar
            params: Parâmetros para a query (para prepared statements)
        
        Returns:
            Resultado da query (formato específico do driver)
        
        Raises:
            ExecutionException: Se ocorrer erro na execução
        """
        pass
    
    @abstractmethod
    def execute_command(self, command: str, params: Optional[Dict] = None) -> int:
        """
        Executa um comando que modifica dados (INSERT, UPDATE, DELETE).
        
        Args:
            command: Comando SQL a executar
            params: Parâmetros para o comando
        
        Returns:
            Número de linhas afetadas
        """
        pass
    
    @abstractmethod
    def fetch_all(self, query: str, params: Optional[Dict] = None) -> list:
        """
        Executa query e retorna todas as linhas.
        
        Args:
            query: Query SQL a executar
            params: Parâmetros para a query
        
        Returns:
            Lista de dicionários representando as linhas
        """
        pass
    
    @abstractmethod
    def fetch_one(self, query: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Executa query e retorna apenas a primeira linha.
        
        Args:
            query: Query SQL a executar
            params: Parâmetros para a query
        
        Returns:
            Dicionário representando a primeira linha ou None
        """
        pass
    
    @abstractmethod
    def fetch_many(self, query: str, size: int, 
                   params: Optional[Dict] = None) -> list:
        """
        Executa query e retorna um número específico de linhas.
        
        Args:
            query: Query SQL a executar
            size: Número máximo de linhas a retornar
            params: Parâmetros para a query
        
        Returns:
            Lista de dicionários representando as linhas
        """
        pass
    
    @abstractmethod
    def get_table_columns(self, table_name: str) -> Dict[str, str]:
        """
        Retorna informações sobre as colunas de uma tabela.
        
        Args:
            table_name: Nome da tabela
        
        Returns:
            Dicionário com nome da coluna como chave e tipo como valor
        """
        pass
    
    @abstractmethod
    def get_connection_string(self) -> str:
        """
        Retorna a string de conexão (sem credenciais exposto em logs).
        
        Returns:
            String de conexão formatada
        """
        pass
    
    @property
    def is_connected(self) -> bool:
        """Retorna se a conexão está ativa."""
        return self._is_connected
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False
    
    def __repr__(self) -> str:
        """Representação em string da conexão."""
        status = "CONECTADO" if self._is_connected else "DESCONECTADO"
        return (f"<{self.__class__.__name__} "
                f"{self.config.host}:{self.config.port} "
                f"status={status}>")
