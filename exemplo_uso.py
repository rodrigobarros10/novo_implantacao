"""
Exemplo de uso do Sistema ETL - Demonstra como integrar tudo junto.

Exemplo 1: Leitura de dados com Pandas
Exemplo 2: Processamento com PySpark
Exemplo 3: Validação com Pydantic
"""

from core.connections.factory import ConnectionFactory, _register_default_drivers
from core.connections.base import ConnectionConfig
from core.engines.pandas_engine import PandasEngine
from models.schemas.produto import ProdutoSchema
from utils.logger import get_logger

logger = get_logger(__name__)

# Registrar drivers disponíveis
_register_default_drivers()


def exemplo_1_pandas():
    """
    Exemplo 1: Ler dados de MySQL com Pandas e validar com Pydantic.
    """
    logger.info("=" * 80)
    logger.info("EXEMPLO 1: Leitura com Pandas + Validação com Pydantic")
    logger.info("=" * 80)
    
    try:
        # Criar configuração de conexão
        config = ConnectionConfig(
            host="localhost",
            port=3306,
            database="seu_banco",
            username="seu_usuario",
            password="sua_senha",
            connection_type="mysql",
            timeout=30
        )
        
        # Factory cria a conexão correta
        connection = ConnectionFactory.create_connection(config)
        
        # Testar conexão
        if connection.test_connection():
            logger.info("✅ Conexão MySQL testada com sucesso!")
        
        # Criar engine Pandas
        engine = PandasEngine(connection)
        
        # Ler dados da query
        query = """
            SELECT 
                idproduto as id,
                descricaoproduto as descricaocompleta,
                descricaocurta as descricaoreduzida,
                valorvenda1 as precovenda,
                estoqueloja as estoque,
                statusproduto as ativo
            FROM produto
            LIMIT 10
        """
        
        df = engine.read_data(query)
        logger.info(f"Dados lidos: {len(df)} linhas")
        
        # Exibir amostra
        engine.show(df, n_rows=5)
        
        # Validar com Pydantic (conversão para dict)
        logger.info("Validando dados com Pydantic...")
        produtos_validados = []
        
        for _, row in df.iterrows():
            try:
                produto = ProdutoSchema(
                    id=int(row['id']),
                    descricaocompleta=row['descricaocompleta'],
                    descricaoreduzida=row['descricaoreduzida'],
                    unidade="UN",
                    precovenda=float(row['precovenda']),
                    ativo=bool(row['ativo']),
                    estoque=float(row['estoque'])
                )
                produtos_validados.append(produto)
            except Exception as e:
                logger.warning(f"Erro ao validar produto {row.get('id')}: {str(e)}")
        
        logger.info(f"✅ {len(produtos_validados)} produtos validados com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro no exemplo: {str(e)}")


def exemplo_2_postgresql():
    """
    Exemplo 2: Ler dados de PostgreSQL com Factory Pattern.
    """
    logger.info("=" * 80)
    logger.info("EXEMPLO 2: Factory Pattern com PostgreSQL")
    logger.info("=" * 80)
    
    try:
        # Factory detecta automaticamente o tipo de banco
        config = ConnectionConfig(
            host="localhost",
            port=5432,
            database="seu_banco",
            username="seu_usuario",
            password="sua_senha",
            connection_type="postgresql",  # Factory escolhe PostgreSQL
            timeout=30
        )
        
        connection = ConnectionFactory.create_connection(config)
        
        logger.info(f"Tipo de conexão criada: {type(connection).__name__}")
        logger.info(f"String de conexão: {connection.get_connection_string()}")
        
        # Testar
        if connection.test_connection():
            logger.info("✅ Conexão PostgreSQL validada!")
    
    except Exception as e:
        logger.error(f"Erro no exemplo: {str(e)}")


def exemplo_3_drivers_suportados():
    """
    Exemplo 3: Listar drivers suportados.
    """
    logger.info("=" * 80)
    logger.info("EXEMPLO 3: Drivers Suportados")
    logger.info("=" * 80)
    
    drivers = ConnectionFactory.get_supported_drivers()
    logger.info(f"Drivers disponíveis: {', '.join(drivers)}")
    
    for driver in drivers:
        is_supported = ConnectionFactory.is_driver_supported(driver)
        logger.info(f"  ✅ {driver.upper()}")


def exemplo_4_validacao_pydantic():
    """
    Exemplo 4: Validação detalhada de Pydantic.
    """
    logger.info("=" * 80)
    logger.info("EXEMPLO 4: Validação com Pydantic")
    logger.info("=" * 80)
    
    # Produto válido
    try:
        produto_ok = ProdutoSchema(
            id=1,
            codigobarras="12345678901234",
            descricaocompleta="Arroz Integral 5kg",
            unidade="KG",
            precovenda=25.50,
            estoque=100,
            ncm="10061000",
            ativo=True
        )
        logger.info(f"✅ Produto válido criado: {produto_ok.descricaocompleta}")
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
    
    # Produto inválido - NCM errado
    try:
        produto_erro = ProdutoSchema(
            id=2,
            descricaocompleta="Leite Integral 1L",
            unidade="L",
            precovenda=5.50,
            ncm="INVALIDO",  # NCM deve ter 8 dígitos
            ativo=True
        )
    except Exception as e:
        logger.warning(f"❌ Validação falhou (esperado): {str(e)}")


if __name__ == "__main__":
    logger.info("\n\n")
    logger.info("🚀 SISTEMA ETL - EXEMPLOS DE USO\n")
    
    # Executar exemplos
    exemplo_3_drivers_suportados()
    exemplo_4_validacao_pydantic()
    
    # Exemplos que precisam de conexões reais (comentados por padrão)
    # exemplo_1_pandas()
    # exemplo_2_postgresql()
    
    logger.info("\n" + "="*80)
    logger.info("✅ Exemplos concluídos!\n")
