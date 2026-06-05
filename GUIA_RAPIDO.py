"""
GUIA RÁPIDO DE REFERÊNCIA - Sistema ETL
Consulte este arquivo para uso rápido do sistema
"""

GUIA_RAPIDO = '''
╔══════════════════════════════════════════════════════════════════════════════╗
║               SISTEMA ETL - GUIA RÁPIDO DE REFERÊNCIA                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│ 1. INICIAR O SISTEMA                                                         │
└──────────────────────────────────────────────────────────────────────────────┘

# Terminal 1: Banco de Dados
$ docker-compose up -d

# Terminal 2: Interface Web
$ source venv/bin/activate
$ streamlit run main.py

→ Acessa em: http://localhost:8501


┌──────────────────────────────────────────────────────────────────────────────┐
│ 2. CADASTRAR CONEXÃO (via Interface)                                         │
└──────────────────────────────────────────────────────────────────────────────┘

1. Clique em "🔌 Conexões"
2. Clique em "➕ Nova Conexão"
3. Preencha:
   - Nome: minha_conexao_origem
   - Tipo: MySQL / PostgreSQL / MSSQL / Oracle
   - Host: localhost (ou IP do servidor)
   - Porta: 3306 (MySQL) / 5432 (PG) / 1433 (MSSQL) / 1521 (Oracle)
   - Banco: nome_do_banco
   - Usuário: seu_usuario
   - Senha: sua_senha
4. Clique em "✅ Criar Conexão"
5. Sistema automaticamente testa a conexão
6. Se OK, aparece "✅ Teste bem-sucedido"


┌──────────────────────────────────────────────────────────────────────────────┐
│ 3. USAR EM CÓDIGO PYTHON                                                     │
└──────────────────────────────────────────────────────────────────────────────┘

# Opção A: Conexão direta
────────────────────────────

from core.connections.factory import ConnectionFactory, _register_default_drivers
from core.connections.base import ConnectionConfig

# Registrar drivers
_register_default_drivers()

# Configurar
config = ConnectionConfig(
    host='localhost',
    port=3306,
    database='supermercado',
    username='admin',
    password='senha123',
    connection_type='mysql'
)

# Factory cria a conexão correta automaticamente
connection = ConnectionFactory.create_connection(config)

# Testar
connection.test_connection()

# Usar
dados = connection.fetch_all('SELECT * FROM produto LIMIT 10')


# Opção B: Com Engine Pandas
─────────────────────────────

from core.engines.pandas_engine import PandasEngine

engine = PandasEngine(connection)
df = engine.read_data('SELECT * FROM produto WHERE ativo = true')

# Operações Pandas
df_filtrado = engine.filter(df, df['preco'] > 10)
df_agrupado = engine.group_by(df, ['categoria'])

# Exibir
engine.show(df, n_rows=5)


# Opção C: Com Engine Spark (grandes volumes)
───────────────────────────────────────────────

from core.engines.spark_engine import SparkEngine

engine = SparkEngine(connection, master='local[*]')
df = engine.read_data('SELECT * FROM produto')

# Mesmas operações, mas distribuídas!
df_filtrado = engine.filter(df, df.preco > 10)

# Mostrar schema
print(engine.get_schema(df))


# Opção D: Validar com Pydantic
────────────────────────────────

from models.schemas.produto import ProdutoSchema

produto = ProdutoSchema(
    id=1,
    codigobarras='12345678901234',
    descricaocompleta='Arroz Integral 5kg',
    unidade='KG',
    precovenda=25.50,
    ncm='10061000',
    ativo=True
)

# Validação automática!
# Se algo errado → exceção ValueError
# Se tudo certo → produto pronto para usar


┌──────────────────────────────────────────────────────────────────────────────┐
│ 4. REFERÊNCIA RÁPIDA DE MÉTODOS                                              │
└──────────────────────────────────────────────────────────────────────────────┘

CONEXÃO (DatabaseConnection)
─────────────────────────────────

connection.connect()                           # Conectar
connection.disconnect()                        # Desconectar
connection.test_connection()                   # Testar
connection.fetch_all(query)                    # Ler todas as linhas
connection.fetch_one(query)                    # Primeira linha
connection.fetch_many(query, 100)              # 100 linhas
connection.execute_command(insert_sql)         # INSERT/UPDATE/DELETE
connection.get_table_columns(table_name)       # Info de colunas
connection.get_connection_string()              # String de conexão
connection.is_connected                        # Status


ENGINE (ProcessingEngine)
──────────────────────────

engine.read_data(query)                        # Ler dados
engine.write_data(df, table_name)              # Escrever dados
engine.filter(df, condition)                   # Filtrar
engine.transform(df, funcao)                   # Transformar
engine.join(left, right, on='id')              # Join
engine.group_by(df, ['coluna'])                # Agrupar
engine.aggregate(grouped, {'col': 'sum'})      # Agregar
engine.persist(df)                             # Cache
engine.count(df)                               # Contar linhas
engine.show(df, n_rows=10)                     # Exibir amostra
engine.get_schema(df)                          # Schema


PYDANTIC (Schemas)
───────────────────

from models.schemas.produto import ProdutoSchema

# Criação (com validação automática)
produto = ProdutoSchema(...)

# Exportar
dict = produto.model_dump()
json = produto.model_dump_json()

# Importar
produto = ProdutoSchema(**dict)


FACTORY (Conexões)
────────────────────

ConnectionFactory.get_supported_drivers()      # Listar drivers
ConnectionFactory.is_driver_supported('mysql')  # Verificar driver
ConnectionFactory.create_connection(config)    # Criar conexão


┌──────────────────────────────────────────────────────────────────────────────┐
│ 5. TIPOS DE BANCO SUPORTADOS                                                 │
└──────────────────────────────────────────────────────────────────────────────┘

MySQL
─────
connection_type: 'mysql'
porta padrão: 3306
driver: pymysql

PostgreSQL
──────────
connection_type: 'postgresql'
porta padrão: 5432
driver: psycopg2

SQL Server (MSSQL)
──────────────────
connection_type: 'mssql'
porta padrão: 1433
driver: pyodbc (requer ODBC Driver 17)

Oracle
──────
connection_type: 'oracle'
porta padrão: 1521
driver: cx_Oracle


┌──────────────────────────────────────────────────────────────────────────────┐
│ 6. TROUBLESHOOTING                                                           │
└──────────────────────────────────────────────────────────────────────────────┘

Erro: "Driver 'xyz' não suportado"
→ Verificar connection_type (mysql, postgresql, mssql, oracle)
→ Verificar se drivers estão registrados

Erro: "Conexão recusada"
→ Verificar host, porta, credenciais
→ Verificar se servidor está ativo
→ Testar com ferramentas nativas (mysql, psql, etc)

Erro: "Senha inválida" (criptografia)
→ Gerar nova chave: python -c "from cryptography.fernet import Fernet; 
  print(Fernet.generate_key().decode())"
→ Salvar em ENCRYPTION_KEY no .env
→ Deletar antiga conexão e criar nova

Erro: "Java not found" (Spark)
→ Instalar Java: brew install openjdk
→ Verificar: java -version

Erro: "Streamlit não inicia"
→ Limpar cache: rm -rf ~/.streamlit/
→ Reexecutar: streamlit run main.py

Postgres não inicia (Docker)
→ Verificar se porta 5432 está livre
→ Parar containers: docker-compose down
→ Remover volumes: docker volume rm sistema_etl_etl_postgres_data
→ Reiniciar: docker-compose up -d


┌──────────────────────────────────────────────────────────────────────────────┐
│ 7. EXEMPLOS DE QUERIES COMUNS                                                │
└──────────────────────────────────────────────────────────────────────────────┘

# Extrair Produtos
SELECT 
    id, codigobarras, descricaocompleta, 
    precovenda, estoque, ativo
FROM produto
WHERE ativo = true
LIMIT 1000

# Extrair Clientes
SELECT 
    id, cnpj_cpf, razao, email, 
    telefone, endereco, ativo
FROM cliente
WHERE ativo = true

# Extrair com JOIN
SELECT 
    p.id, p.descricaocompleta,
    f.razao as fornecedor,
    pf.codigoexterno
FROM produto p
LEFT JOIN fornecedor f ON p.idfornecedor = f.id
LEFT JOIN produto_fornecedor pf ON p.id = pf.id_produto

# Extrair Vendas (últimos 30 dias)
SELECT 
    v.id, v.data, v.total,
    c.razao as cliente,
    item.id_produto, item.quantidade, item.preco
FROM venda v
JOIN cliente c ON v.id_cliente = c.id
JOIN item_venda item ON v.id = item.id_venda
WHERE v.data >= DATE_SUB(NOW(), INTERVAL 30 DAY)


┌──────────────────────────────────────────────────────────────────────────────┐
│ 8. FLUXO TÍPICO COMPLETO                                                     │
└──────────────────────────────────────────────────────────────────────────────┘

1. EXTRAIR
   engine.read_data("SELECT * FROM produto_origem")
   
2. VALIDAR
   for row in data:
       ProdutoSchema(**row)  # Valida automaticamente
   
3. TRANSFORMAR
   engine.transform(df, funcao_transformacao)
   
4. CARREGAR
   engine.write_data(df_transformada, "produto_destino")
   
5. MONITORAR
   → Interface mostra linhas processadas, tempo, erros


┌──────────────────────────────────────────────────────────────────────────────┐
│ 9. COMANDOS ÚTEIS                                                            │
└──────────────────────────────────────────────────────────────────────────────┘

# Ver logs
tail -f logs/sistema_etl_*.log

# Testar conexão MySQL
mysql -h localhost -u admin -p -D supermercado -e "SELECT 1"

# Testar conexão PostgreSQL
psql -h localhost -U etl_user -d etl_metadata -c "SELECT 1"

# Ver containers
docker ps

# Ver logs Docker
docker logs sistema_etl_postgres

# Parar sistema
docker-compose down

# Ver código de um arquivo
cat core/connections/postgresql.py

# Rodar testes
pytest tests/test_core.py -v

# Gerar key criptografia
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"


┌──────────────────────────────────────────────────────────────────────────────┐
│ 10. ESTRUTURA DE DIRETÓRIOS (RESUMIDA)                                       │
└──────────────────────────────────────────────────────────────────────────────┘

sistema_etl/
├── core/connections/        ← Factory Pattern
├── core/engines/            ← Strategy Pattern
├── models/schemas/          ← Pydantic Validation
├── db/                      ← Persistência
├── ui/                      ← Interface Streamlit
├── tests/                   ← Testes
└── main.py                  ← Iniciar Streamlit


═══════════════════════════════════════════════════════════════════════════════

📚 Para mais detalhes:
   • README.md - Visão geral do projeto
   • SETUP.md - Guia de instalação completo
   • RESUMO_EXECUTIVO.py - Documentação detalhada
   • Código comentado em cada arquivo

🆘 Dúvidas?
   • Verificar docstrings das classes
   • Ver exemplos em exemplo_uso.py
   • Rodar testes: pytest tests/
   • Checar logs em logs/

═══════════════════════════════════════════════════════════════════════════════
'''

print(GUIA_RAPIDO)

if __name__ == "__main__":
    import os
    
    # Salvar em arquivo
    with open("GUIA_RAPIDO.txt", "w", encoding="utf-8") as f:
        f.write(GUIA_RAPIDO)
    
    print("\\n✅ Guia salvo em GUIA_RAPIDO.txt")
    print("📂 Você também pode abrir este arquivo em seu editor favorito")
