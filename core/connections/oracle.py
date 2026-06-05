"""
Implementação de conexão Oracle.
"""

from typing import Any, Dict, Optional
import cx_Oracle
from core.connections.base import DatabaseConnection, ConnectionConfig
from utils.logger import get_logger
from utils.exceptions import ConnectionException, ConnectionTestFailedError

logger = get_logger(__name__)


class OracleConnection(DatabaseConnection):
    """Implementação de conexão para Oracle."""
    
    def connect(self) -> bool:
        """Estabelece conexão com Oracle."""
        try:
            dsn = cx_Oracle.makedsn(
                self.config.host,
                self.config.port,
                self.config.database
            )
            
            self._connection = cx_Oracle.connect(
                self.config.username,
                self.config.password,
                dsn,
                threaded=True
            )
            
            self._is_connected = True
            logger.info(f"Conectado ao Oracle: {self.get_connection_string()}")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao Oracle: {str(e)}")
            raise ConnectionException(f"Falha ao conectar ao Oracle: {str(e)}")
    
    def disconnect(self) -> None:
        """Encerra conexão com Oracle."""
        if self._connection:
            try:
                self._connection.close()
                self._is_connected = False
                logger.info("Desconectado do Oracle")
            except Exception as e:
                logger.error(f"Erro ao desconectar: {str(e)}")
    
    def test_connection(self) -> bool:
        """Testa conexão com Oracle."""
        try:
            if not self._is_connected:
                self.connect()
            
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1 FROM dual")
            cursor.close()
            logger.info("Teste de conexão Oracle bem-sucedido")
            return True
        except Exception as e:
            raise ConnectionTestFailedError("Oracle", str(e))
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Executa query SELECT."""
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params or {})
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
            cursor = self._connection.cursor()
            cursor.execute(query, params or {})
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
            cursor.execute(query, params or {})
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
            FROM USER_TAB_COLUMNS 
            WHERE TABLE_NAME = UPPER('{table_name}')
            ORDER BY COLUMN_ID
        """
        try:
            result = self.execute_query(query)
            return {row['COLUMN_NAME']: row['DATA_TYPE'] for row in result}
        except Exception as e:
            logger.error(f"Erro ao obter colunas da tabela: {str(e)}")
            raise ConnectionException(f"Erro ao obter metadados: {str(e)}")
    
    def get_connection_string(self) -> str:
        """Retorna string de conexão (sem password)."""
        return f"oracle://{self.config.username}@{self.config.host}:{self.config.port}/{self.config.database}"
