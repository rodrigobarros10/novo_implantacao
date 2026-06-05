"""
Testes unitários para o Sistema ETL.

Testa Factory Pattern, Strategy Pattern, Schemas Pydantic, etc.
"""

import pytest
from decimal import Decimal
from core.connections.factory import ConnectionFactory, _register_default_drivers
from core.connections.base import ConnectionConfig
from models.schemas.produto import ProdutoSchema
from models.schemas.base import BRBaseSchema
from utils.exceptions import EngineNotSupportedError


# Fixture para registrar drivers
@pytest.fixture(autouse=True)
def register_drivers():
    _register_default_drivers()


class TestConnectionFactory:
    \"\"\"Testes para ConnectionFactory (Factory Pattern).\"\""
    
    def test_get_supported_drivers(self):
        \"\"\"Testa se os drivers padrão estão registrados.\"\""
        drivers = ConnectionFactory.get_supported_drivers()
        assert 'postgresql' in drivers
        assert 'mysql' in drivers
        assert 'mssql' in drivers
        assert 'oracle' in drivers
    
    def test_is_driver_supported(self):
        \"\"\"Testa verificação de driver suportado.\"\""
        assert ConnectionFactory.is_driver_supported('postgresql') == True
        assert ConnectionFactory.is_driver_supported('postgresql') == True
        assert ConnectionFactory.is_driver_supported('unsupported_db') == False
    
    def test_create_postgresql_connection(self):
        \"\"\"Testa criação de conexão PostgreSQL.\"\""
        config = ConnectionConfig(
            host='localhost',
            port=5432,
            database='test_db',
            username='test_user',
            password='test_pass',
            connection_type='postgresql'
        )
        
        connection = ConnectionFactory.create_connection(config)
        assert connection is not None
        assert type(connection).__name__ == 'PostgreSQLConnection'
    
    def test_create_mysql_connection(self):
        \"\"\"Testa criação de conexão MySQL.\"\""
        config = ConnectionConfig(
            host='localhost',
            port=3306,
            database='test_db',
            username='test_user',
            password='test_pass',
            connection_type='mysql'
        )
        
        connection = ConnectionFactory.create_connection(config)
        assert connection is not None
        assert type(connection).__name__ == 'MySQLConnection'
    
    def test_create_unsupported_driver(self):
        \"\"\"Testa erro ao criar conexão com driver não suportado.\"\""
        config = ConnectionConfig(
            host='localhost',
            port=1234,
            database='test_db',
            username='test_user',
            password='test_pass',
            connection_type='unsupported'
        )
        
        with pytest.raises(EngineNotSupportedError):
            ConnectionFactory.create_connection(config)


class TestProdutoSchema:
    \"\"\"Testes para validação de Produto com Pydantic.\"\""
    
    def test_produto_valido(self):
        \"\"\"Testa criação de produto válido.\"\""
        produto = ProdutoSchema(
            id=1,
            descricaocompleta='Arroz Integral 5kg',
            unidade='KG',
            precovenda=Decimal('25.50'),
            ativo=True
        )
        
        assert produto.id == 1
        assert produto.descricaocompleta == 'Arroz Integral 5kg'
        assert produto.unidade == 'KG'
        assert produto.precovenda == Decimal('25.50')
        assert produto.ativo == True
    
    def test_produto_id_zero(self):
        \"\"\"Testa validação de ID (deve ser > 0).\"\""
        with pytest.raises(ValueError):
            ProdutoSchema(
                id=0,
                descricaocompleta='Teste',
                unidade='UN',
                precovenda=Decimal('10.00')
            )
    
    def test_produto_descricao_curta(self):
        \"\"\"Testa validação de descrição (mínimo 3 caracteres).\"\""
        with pytest.raises(ValueError):
            ProdutoSchema(
                id=1,
                descricaocompleta='AB',  # Muito curto
                unidade='UN',
                precovenda=Decimal('10.00')
            )
    
    def test_produto_preco_zero(self):
        \"\"\"Testa validação de preço (deve ser > 0).\"\""
        with pytest.raises(ValueError):
            ProdutoSchema(
                id=1,
                descricaocompleta='Produto Teste',
                unidade='UN',
                precovenda=Decimal('0.00')  # Inválido
            )
    
    def test_produto_ncm_invalido(self):
        \"\"\"Testa validação de NCM (deve ter 8 dígitos).\"\"\"\n        with pytest.raises(ValueError):
            ProdutoSchema(
                id=1,
                descricaocompleta='Produto Teste',
                unidade='UN',
                precovenda=Decimal('10.00'),
                ncm='1234'  # NCM deve ter 8 dígitos
            )
    
    def test_produto_unidade_invalida(self):
        \"\"\"Testa validação de unidade.\"\"\"\n        with pytest.raises(ValueError):
            ProdutoSchema(
                id=1,
                descricaocompleta='Produto Teste',
                unidade='INVALIDA',
                precovenda=Decimal('10.00')
            )
    
    def test_produto_estoque_maior_maximo(self):
        \"\"\"Testa validação de coerência estoque.\"\"\"\n        with pytest.raises(ValueError):
            ProdutoSchema(
                id=1,
                descricaocompleta='Produto Teste',
                unidade='UN',
                precovenda=Decimal('10.00'),
                estoquemaximo=Decimal('100'),
                estoque=Decimal('150')  # Maior que máximo
            )


class TestBRBaseSchema:
    \"\"\"Testes para validadores do schema base.\"\"\"\n    
    def test_validate_cnpj_valido(self):
        \"\"\"Testa validação de CNPJ.\"\"\"\n        cnpj = BRBaseSchema.validate_cnpj('11222333000181')
        assert '.' in cnpj
        assert '/' in cnpj
        assert '-' in cnpj
    
    def test_validate_cpf_valido(self):
        \"\"\"Testa validação de CPF.\"\"\"\n        cpf = BRBaseSchema.validate_cpf('12345678901')
        assert '.' in cpf
        assert '-' in cpf
    
    def test_validate_email(self):
        \"\"\"Testa validação de email.\"\"\"\n        email_valido = BRBaseSchema.validate_email('usuario@example.com')
        assert email_valido == 'usuario@example.com'
        
        with pytest.raises(ValueError):
            BRBaseSchema.validate_email('email_invalido')
    
    def test_validate_cep(self):
        \"\"\"Testa validação de CEP.\"\"\"\n        cep = BRBaseSchema.validate_cep('01310100')
        assert '-' in cep
    
    def test_normalize_string(self):
        \"\"\"Testa normalização de string.\"\"\"\n        resultado = BRBaseSchema.normalize_string('  texto   com   espaços  ')
        assert resultado == 'texto com espaços'


if __name__ == '__main__':
    # Executar testes com pytest
    pytest.main([__file__, '-v', '--tb=short'])
