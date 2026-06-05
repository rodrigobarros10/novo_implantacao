"""
Implementação de conexão PostgreSQL.
"""

from typing import Any, Dict, Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
from core.connections.base import DatabaseConnection, ConnectionConfig
from utils.logger import get_logger
from utils.exceptions import ConnectionException, ConnectionTestFailedError

logger = get_logger(__name__)


class PostgreSQLConnection(DatabaseConnection):
    """Implementação de conexão para PostgreSQL."""
    
    def connect(self) -> bool:
        """Estabelece conexão com PostgreSQL."""
        try:
            self._connection = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                connect_timeout=self.config.timeout,
                options="-c default_transaction_isolation=read_committed"
            )
            self._is_connected = True
            logger.info(f"Conectado ao PostgreSQL: {self.get_connection_string()}")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao PostgreSQL: {str(e)}")
            raise ConnectionException(f"Falha ao conectar ao PostgreSQL: {str(e)}")
    
    def disconnect(self) -> None:
        """Encerra conexão com PostgreSQL."""
        if self._connection:
            try:
                self._connection.close()
                self._is_connected = False
                logger.info("Desconectado do PostgreSQL")
            except Exception as e:
                logger.error(f"Erro ao desconectar: {str(e)}")
    
    def test_connection(self) -> bool:
        """Testa conexão com PostgreSQL."""
        try:
            if not self._is_connected:
                self.connect()
            
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            logger.info("Teste de conexão PostgreSQL bem-sucedido")
            return True
        except Exception as e:
            raise ConnectionTestFailedError("PostgreSQL", str(e))
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Executa query SELECT."""
        try:
            cursor = self._connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params or {})
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            logger.error(f"Erro ao executar query: {str(e)}")
            raise ConnectionException(f"Erro na execução: {str(e)}")
    
    def execute_command(self, command: str, params: Optional[Dict] = None) -> int:
        """Executa INSERT, UPDATE ou DELETE."""
        try:
            cursor = self._connection.cursor()
            cursor.execute(command, params or {})
            rows_affected = cursor.rowcount
            self._connection.commit()
            cursor.close()
            logger.info(f"Comando executado: {rows_affected} linhas afetadas")
            return rows_affected
        except Exception as e:
            self._connection.rollback()
            logger.error(f"Erro ao executar comando: {str(e)}")
            raise ConnectionException(f"Erro na execução: {str(e)}")
    
    def fetch_all(self, query: str, params: Optional[Dict] = None) -> list:
        """Retorna todas as linhas."""
        return self.execute_query(query, params)
    
    def fetch_one(self, query: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Retorna apenas a primeira linha."""
        try:
            cursor = self._connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params or {})
            result = cursor.fetchone()
            cursor.close()
            return result
        except Exception as e:
            logger.error(f"Erro ao executar fetch_one: {str(e)}")
            raise ConnectionException(f"Erro na execução: {str(e)}")
    
    def fetch_many(self, query: str, size: int, 
                   params: Optional[Dict] = None) -> list:
        """Retorna um número específico de linhas."""
        try:
            cursor = self._connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params or {})
            result = cursor.fetchmany(size)
            cursor.close()
            return result
        except Exception as e:
            logger.error(f"Erro ao executar fetch_many: {str(e)}")
            raise ConnectionException(f"Erro na execução: {str(e)}")
    
    def get_table_columns(self, table_name: str) -> Dict[str, str]:
        """Retorna informações sobre as colunas da tabela."""
        query = """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """
        try:
            result = self.execute_query(query, (table_name,))
            return {row['column_name']: row['data_type'] for row in result}
        except Exception as e:
            logger.error(f"Erro ao obter colunas da tabela: {str(e)}")
            raise ConnectionException(f"Erro ao obter metadados: {str(e)}")
    
    def get_connection_string(self) -> str:
        """Retorna string de conexão (sem password)."""
        return f"postgresql://{self.config.username}@{self.config.host}:{self.config.port}/{self.config.database}"
