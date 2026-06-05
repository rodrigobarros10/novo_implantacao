"""
Interface abstrata para engines de processamento.

Define o contrato para diferentes estratégias de processamento de dados
(Pandas, PySpark, Polars, etc).
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from core.connections.base import DatabaseConnection
from utils.logger import get_logger

logger = get_logger(__name__)


class ProcessingEngine(ABC):
    """
    Interface abstrata para engines de processamento de dados.
    
    Implementações concretas devem fornecer métodos para:
    - Ler dados de uma conexão
    - Executar transformações
    - Validar dados
    - Escrever resultados
    """
    
    def __init__(self, source_connection: DatabaseConnection, 
                 target_connection: Optional[DatabaseConnection] = None):
        """
        Inicializa o engine de processamento.
        
        Args:
            source_connection: Conexão de origem
            target_connection: Conexão de destino (opcional para read-only)
        """
        self.source_connection = source_connection
        self.target_connection = target_connection
        logger.info(f"Engine '{self.__class__.__name__}' inicializado")
    
    @abstractmethod
    def read_data(self, query: str, params: Optional[Dict] = None) -> Any:
        """
        Lê dados de uma query e retorna em formato nativo do engine.
        
        Args:
            query: Query SQL a executar
            params: Parâmetros da query
        
        Returns:
            Dados em formato nativo do engine (DataFrame, RDD, etc)
        """
        pass
    
    @abstractmethod
    def write_data(self, data: Any, table_name: str, 
                   mode: str = 'append') -> int:
        """
        Escreve dados em uma tabela de destino.
        
        Args:
            data: Dados em formato nativo do engine
            table_name: Nome da tabela de destino
            mode: Modo de escrita ('append', 'overwrite', 'ignore')
        
        Returns:
            Número de linhas escritas
        """
        pass
    
    @abstractmethod
    def transform(self, data: Any, transformation_func) -> Any:
        """
        Aplica uma transformação aos dados.
        
        Args:
            data: Dados em formato nativo do engine
            transformation_func: Função que implementa a transformação
        
        Returns:
            Dados transformados
        """
        pass
    
    @abstractmethod
    def filter(self, data: Any, condition: Any) -> Any:
        """
        Filtra dados baseado em uma condição.
        
        Args:
            data: Dados em formato nativo do engine
            condition: Condição de filtro (syntax específica do engine)
        
        Returns:
            Dados filtrados
        """
        pass
    
    @abstractmethod
    def join(self, left: Any, right: Any, on: str, 
             how: str = 'inner') -> Any:
        """
        Realiza join entre dois datasets.
        
        Args:
            left: Dataset esquerdo
            right: Dataset direito
            on: Coluna(s) para fazer o join
            how: Tipo de join ('inner', 'left', 'right', 'outer')
        
        Returns:
            Dataset resultado do join
        """
        pass
    
    @abstractmethod
    def group_by(self, data: Any, columns: list) -> Any:
        """
        Agrupa dados por colunas especificadas.
        
        Args:
            data: Dados em formato nativo do engine
            columns: Lista de colunas para agrupar
        
        Returns:
            Dados agrupados (GroupBy object específico do engine)
        """
        pass
    
    @abstractmethod
    def aggregate(self, grouped_data: Any, agg_dict: Dict) -> Any:
        """
        Aplica agregações a dados agrupados.
        
        Args:
            grouped_data: Dados agrupados
            agg_dict: Dicionário com agregações {coluna: [função, ...]}
        
        Returns:
            Dados agregados
        """
        pass
    
    @abstractmethod
    def persist(self, data: Any) -> Any:
        """
        Persiste dados em cache/memória para reutilização.
        
        Args:
            data: Dados em formato nativo do engine
        
        Returns:
            Dados persistidos
        """
        pass
    
    @abstractmethod
    def count(self, data: Any) -> int:
        """
        Conta o número de linhas/registros.
        
        Args:
            data: Dados em formato nativo do engine
        
        Returns:
            Número de linhas
        """
        pass
    
    @abstractmethod
    def show(self, data: Any, n_rows: int = 10) -> None:
        """
        Exibe uma amostra dos dados (para debugging).
        
        Args:
            data: Dados em formato nativo do engine
            n_rows: Número de linhas a exibir
        """
        pass
    
    @abstractmethod
    def get_schema(self, data: Any) -> Dict:
        """
        Retorna o schema/estrutura dos dados.
        
        Args:
            data: Dados em formato nativo do engine
        
        Returns:
            Dicionário com informações de schema
        """
        pass
    
    def __repr__(self) -> str:
        """Representação em string do engine."""
        return f"<{self.__class__.__name__} engine>"
