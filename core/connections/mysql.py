"""
Implementação de conexão MySQL.
"""

from typing import Any, Dict, Optional
import pymysql
from pymysql.cursors import DictCursor
from core.connections.base import DatabaseConnection, ConnectionConfig
from utils.logger import get_logger
from utils.exceptions import ConnectionException, ConnectionTestFailedError

logger = get_logger(__name__)


class MySQLConnection(DatabaseConnection):
    """Implementação de conexão para MySQL."""
    
    def connect(self) -> bool:
        """Estabelece conexão com MySQL."""
        try:
            self._connection = pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                connect_timeout=self.config.timeout,
                cursorclass=DictCursor,
                autocommit=True
            )
            self._is_connected = True
            logger.info(f"Conectado ao MySQL: {self.get_connection_string()}")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao MySQL: {str(e)}")
            raise ConnectionException(f"Falha ao conectar ao MySQL: {str(e)}")
    
    def disconnect(self) -> None:
        """Encerra conexão com MySQL."""
        if self._connection:
            try:
                self._connection.close()
                self._is_connected = False
                logger.info("Desconectado do MySQL")
            except Exception as e:
                logger.error(f"Erro ao desconectar: {str(e)}")
    
    def test_connection(self) -> bool:
        """Testa conexão com MySQL."""
        try:
            if not self._is_connected:
                self.connect()
            
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            logger.info("Teste de conexão MySQL bem-sucedido")
            return True
        except Exception as e:
            raise ConnectionTestFailedError("MySQL", str(e))
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Executa query SELECT."""
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params or ())
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
            cursor.execute(command, params or ())
            rows_affected = cursor.rowcount
            cursor.close()
            self._connection.commit()
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
            cursor = self._connection.cursor()
            cursor.execute(query, params or ())
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
            cursor = self._connection.cursor()
            cursor.execute(query, params or ())
            result = cursor.fetchmany(size)
            cursor.close()
            return result
        except Exception as e:
            logger.error(f"Erro ao executar fetch_many: {str(e)}")
            raise ConnectionException(f"Erro na execução: {str(e)}")
    
    def get_table_columns(self, table_name: str) -> Dict[str, str]:
        """Retorna informações sobre as colunas da tabela."""
        query = f"DESCRIBE {table_name}"
        try:
            cursor = self._connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return {row['Field']: row['Type'] for row in result}
        except Exception as e:
            logger.error(f"Erro ao obter colunas da tabela: {str(e)}")
            raise ConnectionException(f"Erro ao obter metadados: {str(e)}")
    
    def get_connection_string(self) -> str:
        """Retorna string de conexão (sem password)."""
        return f"mysql://{self.config.username}@{self.config.host}:{self.config.port}/{self.config.database}"
