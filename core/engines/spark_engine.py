"""
Implementação PySpark para o engine de processamento.

Strategy para processamento distribuído de grandes volumes de dados
usando Apache Spark.
"""

from typing import Any, Optional, Dict, Callable
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col
from core.engines.base import ProcessingEngine
from core.connections.base import DatabaseConnection
from utils.logger import get_logger

logger = get_logger(__name__)


class SparkEngine(ProcessingEngine):
    """Engine de processamento usando PySpark."""
    
    def __init__(self, source_connection: DatabaseConnection,
                 target_connection: Optional[DatabaseConnection] = None,
                 app_name: str = "SistemaETL",
                 master: str = "local[*]"):
        """
        Inicializa o engine Spark.
        
        Args:
            source_connection: Conexão de origem
            target_connection: Conexão de destino
            app_name: Nome da aplicação Spark
            master: Master URL (local[*], yarn, etc)
        """
        super().__init__(source_connection, target_connection)
        
        # Inicializar SparkSession
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .master(master) \
            .config("spark.sql.shuffle.partitions", "200") \
            .config("spark.default.parallelism", "200") \
            .getOrCreate()
        
        logger.info(f"SparkSession criada: {app_name}")
    
    def read_data(self, query: str, params: Optional[Dict] = None) -> DataFrame:
        """Lê dados usando SQL para Spark DataFrame."""
        try:
            logger.info(f"Lendo dados com Spark: {query[:100]}...")
            
            if params:
                query = query.format(**params)
            
            # Lê dados da conexão de origem
            result = self.source_connection.fetch_all(query, params)
            
            # Converter para Spark DataFrame
            if not result:
                logger.warning("Query retornou vazio")
                return self.spark.createDataFrame([], schema="")
            
            df = self.spark.createDataFrame(result)
            
            # Repartição para processamento distribuído
            num_partitions = max(1, self.spark.sparkContext.defaultParallelism)
            df = df.repartition(num_partitions)
            
            logger.info(f"Dados lidos: {df.count()} linhas, "
                       f"{len(df.columns)} colunas, "
                       f"{num_partitions} partições")
            return df
        except Exception as e:
            logger.error(f"Erro ao ler dados: {str(e)}")
            raise
    
    def write_data(self, data: DataFrame, table_name: str,
                   mode: str = 'append') -> int:
        """Escreve dados em tabela de destino."""
        if not self.target_connection:
            raise ValueError("Conexão de destino não configurada")
        
        try:
            logger.info(f"Escrevendo dados Spark em '{table_name}'")
            
            # Converter para Pandas para escrita
            pandas_df = data.toPandas()
            rows_written = len(pandas_df)
            
            # Usar a implementação Pandas para escrita
            from core.engines.pandas_engine import PandasEngine
            pandas_engine = PandasEngine(self.source_connection, self.target_connection)
            pandas_engine.write_data(pandas_df, table_name, mode)
            
            logger.info(f"Dados Spark escritos: {rows_written} linhas")
            return rows_written
        except Exception as e:
            logger.error(f"Erro ao escrever dados: {str(e)}")
            raise
    
    def transform(self, data: DataFrame,
                  transformation_func: Callable) -> DataFrame:
        """Aplica transformação customizada aos dados."""
        try:
            logger.info("Aplicando transformação aos dados Spark")
            result = transformation_func(data)
            logger.info(f"Transformação concluída")
            return result
        except Exception as e:
            logger.error(f"Erro na transformação: {str(e)}")
            raise
    
    def filter(self, data: DataFrame, condition: Any) -> DataFrame:
        """Filtra dados Spark baseado em condição."""
        try:
            logger.info("Aplicando filtro aos dados Spark")
            result = data.filter(condition)
            logger.info(f"Filtro aplicado")
            return result
        except Exception as e:
            logger.error(f"Erro ao filtrar dados: {str(e)}")
            raise
    
    def join(self, left: DataFrame, right: DataFrame,
             on: str, how: str = 'inner') -> DataFrame:
        """Realiza join entre Spark DataFrames."""
        try:
            logger.info(f"Realizando {how} join em '{on}'")
            result = left.join(right, on=on, how=how)
            logger.info(f"Join concluído")
            return result
        except Exception as e:
            logger.error(f"Erro no join: {str(e)}")
            raise
    
    def group_by(self, data: DataFrame, columns: list):
        """Agrupa dados Spark por colunas."""
        try:
            logger.info(f"Agrupando por {columns}")
            return data.groupBy(columns)
        except Exception as e:
            logger.error(f"Erro ao agrupar: {str(e)}")
            raise
    
    def aggregate(self, grouped_data, agg_dict: Dict) -> DataFrame:
        """Aplica agregações a dados Spark agrupados."""
        try:
            logger.info(f"Aplicando agregações: {agg_dict}")
            result = grouped_data.agg(agg_dict)
            logger.info(f"Agregações concluídas")
            return result
        except Exception as e:
            logger.error(f"Erro nas agregações: {str(e)}")
            raise
    
    def persist(self, data: DataFrame) -> DataFrame:
        """Persiste dados em cache."""
        try:
            data.persist()
            logger.info("Dados persistidos em cache")
            return data
        except Exception as e:
            logger.error(f"Erro ao persistir dados: {str(e)}")
            raise
    
    def count(self, data: DataFrame) -> int:
        """Conta linhas."""
        return data.count()
    
    def show(self, data: DataFrame, n_rows: int = 10) -> None:
        """Exibe amostra dos dados Spark."""
        print("\n" + "="*80)
        data.show(n_rows, truncate=False)
        print(f"\nTotal de linhas: {data.count()}")
        print("="*80 + "\n")
    
    def get_schema(self, data: DataFrame) -> Dict:
        """Retorna schema do Spark DataFrame."""
        return {
            'columns': data.columns,
            'types': {field.name: str(field.dataType) for field in data.schema.fields},
            'shape': (data.count(), len(data.columns))
        }
    
    def stop(self):
        """Encerra a SparkSession."""
        self.spark.stop()
        logger.info("SparkSession encerrada")
