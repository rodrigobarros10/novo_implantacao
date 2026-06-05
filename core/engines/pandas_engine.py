"""
Implementação Pandas para o engine de processamento.

Strategy para processamento de dados em volumes pequenos a médios
usando Pandas com dados em memória.
"""

from typing import Any, Optional, Dict, Callable
import pandas as pd
import numpy as np
from core.engines.base import ProcessingEngine
from core.connections.base import DatabaseConnection
from utils.logger import get_logger

logger = get_logger(__name__)


class PandasEngine(ProcessingEngine):
    """Engine de processamento usando Pandas."""
    
    def __init__(self, source_connection: DatabaseConnection,
                 target_connection: Optional[DatabaseConnection] = None):
        """Inicializa o engine Pandas."""
        super().__init__(source_connection, target_connection)
        self.chunk_size = 10000  # Para processar grandes datasets em chunks
    
    def read_data(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """Lê dados usando SQL para Pandas."""
        try:
            logger.info(f"Lendo dados com Pandas: {query[:100]}...")
            
            if params:
                # Substituir parâmetros na query
                query = query.format(**params)
            
            result = self.source_connection.fetch_all(query, params)
            df = pd.DataFrame(result)
            
            logger.info(f"Dados lidos: {len(df)} linhas, {len(df.columns)} colunas")
            return df
        except Exception as e:
            logger.error(f"Erro ao ler dados: {str(e)}")
            raise
    
    def write_data(self, data: pd.DataFrame, table_name: str,
                   mode: str = 'append') -> int:
        """Escreve dados em tabela de destino."""
        if not self.target_connection:
            raise ValueError("Conexão de destino não configurada")
        
        try:
            logger.info(f"Escrevendo {len(data)} linhas em '{table_name}'")
            
            # Converter DataFrame para lista de dicionários
            records = data.to_dict('records')
            rows_written = 0
            
            for record in records:
                # Construir INSERT statement dinamicamente
                columns = ', '.join(record.keys())
                values = ', '.join(['%s'] * len(record))
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
                
                self.target_connection.execute_command(sql, tuple(record.values()))
                rows_written += 1
            
            logger.info(f"Dados escritos com sucesso: {rows_written} linhas")
            return rows_written
        except Exception as e:
            logger.error(f"Erro ao escrever dados: {str(e)}")
            raise
    
    def transform(self, data: pd.DataFrame,
                  transformation_func: Callable) -> pd.DataFrame:
        """Aplica transformação customizada aos dados."""
        try:
            logger.info("Aplicando transformação aos dados")
            result = transformation_func(data)
            logger.info(f"Transformação concluída: {len(result)} linhas")
            return result
        except Exception as e:
            logger.error(f"Erro na transformação: {str(e)}")
            raise
    
    def filter(self, data: pd.DataFrame, condition: Any) -> pd.DataFrame:
        """Filtra dados baseado em condição Pandas."""
        try:
            logger.info("Aplicando filtro aos dados")
            result = data[condition]
            logger.info(f"Filtro aplicado: {len(result)} linhas restantes")
            return result
        except Exception as e:
            logger.error(f"Erro ao filtrar dados: {str(e)}")
            raise
    
    def join(self, left: pd.DataFrame, right: pd.DataFrame,
             on: str, how: str = 'inner') -> pd.DataFrame:
        """Realiza join entre DataFrames."""
        try:
            logger.info(f"Realizando {how} join em '{on}'")
            result = pd.merge(left, right, on=on, how=how)
            logger.info(f"Join concluído: {len(result)} linhas")
            return result
        except Exception as e:
            logger.error(f"Erro no join: {str(e)}")
            raise
    
    def group_by(self, data: pd.DataFrame, columns: list):
        """Agrupa dados por colunas."""
        try:
            logger.info(f"Agrupando por {columns}")
            return data.groupby(columns)
        except Exception as e:
            logger.error(f"Erro ao agrupar: {str(e)}")
            raise
    
    def aggregate(self, grouped_data, agg_dict: Dict) -> pd.DataFrame:
        """Aplica agregações a dados agrupados."""
        try:
            logger.info(f"Aplicando agregações: {agg_dict}")
            result = grouped_data.agg(agg_dict).reset_index()
            logger.info(f"Agregações concluídas: {len(result)} linhas")
            return result
        except Exception as e:
            logger.error(f"Erro nas agregações: {str(e)}")
            raise
    
    def persist(self, data: pd.DataFrame) -> pd.DataFrame:
        """Em Pandas, persist é um no-op (dados já estão em memória)."""
        return data
    
    def count(self, data: pd.DataFrame) -> int:
        """Conta linhas."""
        return len(data)
    
    def show(self, data: pd.DataFrame, n_rows: int = 10) -> None:
        """Exibe amostra dos dados."""
        print("\n" + "="*80)
        print(data.head(n_rows).to_string())
        print(f"\nTotal de linhas: {len(data)}")
        print(f"Colunas: {list(data.columns)}")
        print("="*80 + "\n")
    
    def get_schema(self, data: pd.DataFrame) -> Dict:
        """Retorna schema do DataFrame."""
        return {
            'columns': list(data.columns),
            'types': {col: str(dtype) for col, dtype in zip(data.columns, data.dtypes)},
            'shape': data.shape,
            'memory_usage': data.memory_usage(deep=True).sum()
        }
