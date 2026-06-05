"""
Exceptions customizadas do sistema ETL.

Módulo centralizado para definir exceções específicas do domínio,
facilitando tratamento de erros granular e mais informativo.
"""


class ETLException(Exception):
    """Exceção base do sistema ETL."""
    
    def __init__(self, message: str, code: str = "ETL_ERROR"):
        """
        Inicializa a exceção base.
        
        Args:
            message: Mensagem de erro descritiva
            code: Código único para identificar o tipo de erro
        """
        self.message = message
        self.code = code
        super().__init__(self.message)


class ConnectionException(ETLException):
    """Exceção relacionada a conexões com banco de dados."""
    pass


class ConnectionNotFoundError(ConnectionException):
    """Exceção quando uma conexão não é encontrada."""
    
    def __init__(self, connection_id: str):
        super().__init__(
            f"Conexão com ID '{connection_id}' não foi encontrada.",
            "CONNECTION_NOT_FOUND"
        )


class ConnectionTestFailedError(ConnectionException):
    """Exceção quando o teste de conexão falha."""
    
    def __init__(self, connection_name: str, error: str):
        super().__init__(
            f"Falha ao testar conexão '{connection_name}': {error}",
            "CONNECTION_TEST_FAILED"
        )


class InvalidConnectionConfigError(ConnectionException):
    """Exceção quando a configuração de conexão é inválida."""
    
    def __init__(self, message: str):
        super().__init__(
            f"Configuração de conexão inválida: {message}",
            "INVALID_CONNECTION_CONFIG"
        )


class EngineException(ETLException):
    """Exceção relacionada aos engines de processamento."""
    pass


class EngineNotSupportedError(EngineException):
    """Exceção quando um engine não é suportado."""
    
    def __init__(self, engine_type: str):
        super().__init__(
            f"Engine '{engine_type}' não é suportado.",
            "ENGINE_NOT_SUPPORTED"
        )


class ValidationException(ETLException):
    """Exceção relacionada à validação de dados."""
    pass


class SchemaValidationError(ValidationException):
    """Exceção quando os dados não passam na validação do schema."""
    
    def __init__(self, entity: str, errors: str):
        super().__init__(
            f"Falha na validação do schema para '{entity}': {errors}",
            "SCHEMA_VALIDATION_ERROR"
        )


class PipelineException(ETLException):
    """Exceção relacionada à pipeline ETL."""
    pass


class PipelineExecutionError(PipelineException):
    """Exceção quando a execução da pipeline falha."""
    
    def __init__(self, job_id: str, step: str, error: str):
        super().__init__(
            f"Falha na execução da pipeline job_id={job_id} "
            f"no passo '{step}': {error}",
            "PIPELINE_EXECUTION_ERROR"
        )
