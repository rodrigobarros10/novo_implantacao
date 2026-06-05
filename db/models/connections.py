"""
Modelos SQLAlchemy para persistência de metadados.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, LargeBinary
from sqlalchemy.dialects.postgresql import JSON
from db.base import Base
from utils.logger import get_logger

logger = get_logger(__name__)


class ConnectionModel(Base):
    """
    Modelo para armazenar configurações de conexões.
    
    Tabela que persiste as credenciais e configurações de conexão
    com diferentes bancos de dados de origem e destino.
    """
    __tablename__ = 'connections'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    connection_type = Column(String(50), nullable=False)  # mysql, postgresql, mssql, oracle
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    database = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(LargeBinary, nullable=False)  # Criptografado
    timeout = Column(Integer, default=30)
    pool_size = Column(Integer, default=5)
    extra_params = Column(JSON, nullable=True)  # Parâmetros adicionais
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tested_at = Column(DateTime, nullable=True)
    is_valid = Column(Boolean, default=False)
    last_error = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    
    def __repr__(self):
        return f"<Connection {self.name} ({self.connection_type})>"


class JobModel(Base):
    """
    Modelo para armazenar configurações de jobs ETL.
    
    Define quais scripts SQL são executados e para qual entidade,
    permitindo agendamento e reutilização.
    """
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Conexões
    source_connection_id = Column(Integer, nullable=False, index=True)
    target_connection_id = Column(Integer, nullable=False, index=True)
    
    # Configuração
    entity = Column(String(50), nullable=False)  # produto, cliente, fornecedor, etc
    extract_query = Column(Text, nullable=False)  # SQL de extração
    engine_type = Column(String(20), default='pandas')  # pandas ou spark
    
    # Transformações
    transformations = Column(JSON, nullable=True)  # Configurações de transformação
    validations = Column(JSON, nullable=True)  # Regras de validação
    
    # Agendamento
    schedule_cron = Column(String(50), nullable=True)  # Ex: "0 2 * * *" para 2AM diariamente
    
    # Auditoria
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    is_scheduled = Column(Boolean, default=False)
    last_execution = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Job {self.name} ({self.entity})>"


class ExecutionModel(Base):
    """
    Modelo para armazenar histórico de execuções de jobs.
    
    Registra cada execução de um job com status, tempos e erros.
    """
    __tablename__ = 'executions'
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, nullable=False, index=True)
    
    # Status
    status = Column(String(20), default='RUNNING')  # RUNNING, SUCCESS, FAILED, PARTIAL
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    
    # Resultados
    rows_extracted = Column(Integer, default=0)
    rows_loaded = Column(Integer, default=0)
    rows_failed = Column(Integer, default=0)
    
    # Logs
    log_output = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Performance
    duration_seconds = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<Execution job_id={self.job_id} status={self.status}>"
