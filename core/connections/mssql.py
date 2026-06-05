"""
Implementação de conexão Microsoft SQL Server.
"""

from typing import Any, Dict, Optional
import pyodbc
from core.connections.base import DatabaseConnection, ConnectionConfig
from utils.logger import get_logger
from utils.exceptions import ConnectionException, ConnectionTestFailedError

logger = get_logger(__name__)


class MSSQLConnection(DatabaseConnection):
    """Implementação de conexão para SQL Server."""
    
    def connect(self) -> bool:
        """Estabelece conexão com SQL Server."""
        try:
            connection_string = (
                f"Driver={{ODBC Driver 17 for SQL Server}};"
                f"Server={self.config.host},{self.config.port};"
                f"Database={self.config.database};"
                f"UID={self.config.username};"
                f"PWD={self.config.password};"
                f"Timeout={self.config.timeout};"
            )
            
            self._connection = pyodbc.connect(connection_string, autocommit=True)
            self._is_connected = True
            logger.info(f"Conectado ao SQL Server: {self.get_connection_string()}")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao SQL Server: {str(e)}")
            raise ConnectionException(f"Falha ao conectar ao SQL Server: {str(e)}")
    
    def disconnect(self) -> None:
        """Encerra conexão com SQL Server."""
        if self._connection:
            try:
                self._connection.close()
                self._is_connected = False
                logger.info("Desconectado do SQL Server")
            except Exception as e:
                logger.error(f"Erro ao desconectar: {str(e)}")
    
    def test_connection(self) -> bool:
        """Testa conexão com SQL Server."""
        try:
            if not self._is_connected:
                self.connect()
            
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            logger.info("Teste de conexão SQL Server bem-sucedido")
            return True
        except Exception as e:
            raise ConnectionTestFailedError("SQL Server", str(e))
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Executa query SELECT."""
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params or ())
            columns = [desc[0] for desc in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
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
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            cursor.close()
            return dict(zip(columns, row)) if row else None
        except Exception as e:
            logger.error(f"Erro ao executar fetch_one: {str(e)}")
            raise ConnectionException(f"Erro na execução: {str(e)}")
    
    def fetch_many(self, query: str, size: int, 
                   params: Optional[Dict] = None) -> list:
        """Retorna um número específico de linhas."""
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params or ())
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchmany(size)
            result = [dict(zip(columns, row)) for row in rows]
            cursor.close()
            return result
        except Exception as e:
            logger.error(f"Erro ao executar fetch_many: {str(e)}")
            raise ConnectionException(f"Erro na execução: {str(e)}")
    
    def get_table_columns(self, table_name: str) -> Dict[str, str]:
        """Retorna informações sobre as colunas da tabela."""
        query = f"""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
        """
        try:
            result = self.execute_query(query)
            return {row['COLUMN_NAME']: row['DATA_TYPE'] for row in result}
        except Exception as e:
            logger.error(f"Erro ao obter colunas da tabela: {str(e)}")
            raise ConnectionException(f"Erro ao obter metadados: {str(e)}")
    
    def get_connection_string(self) -> str:
        """Retorna string de conexão (sem password)."""
        return f"mssql://{self.config.username}@{self.config.host}:{self.config.port}/{self.config.database}"
