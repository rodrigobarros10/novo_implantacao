"""
ARQUITETURA E FLUXO DO SISTEMA ETL

Visualize como todos os componentes se conectam
"""

ARQUITETURA = r'''
╔══════════════════════════════════════════════════════════════════════════════╗
║                      ARQUITETURA SISTEMA ETL                                ║
║                  Design Patterns & Fluxo de Dados                           ║
╚══════════════════════════════════════════════════════════════════════════════╝


┌─────────────────────────────────────────────────────────────────────────────┐
│                        CAMADA DE APRESENTAÇÃO                               │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    STREAMLIT (Interface Web)                        │   │
│  │  ┌────────────┬────────────┬────────────┬────────────┐              │   │
│  │  │   Home    │Conexões  │   Jobs   │ Execuções  │              │   │
│  │  │ Dashboard │Cadastro  │Config    │Histórico   │              │   │
│  │  └────────────┴────────────┴────────────┴────────────┘              │   │
│  │                                                                     │   │
│  │  Tasks:                                                             │   │
│  │  • Form de conexão (teste de credenciais)                           │   │
│  │  • CRUD de Jobs                                                     │   │
│  │  • Monitoramento em tempo real                                      │   │
│  │  • Visualização de erros                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                   ↓
                                   ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CAMADA DE PERSISTÊNCIA                               │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              SQLAlchemy + PostgreSQL (Metadados)                    │   │
│  │  ┌──────────────┬──────────────┬──────────────────────────┐         │   │
│  │  │  Connections │    Jobs      │     Executions           │         │   │
│  │  ├──────────────┼──────────────┼──────────────────────────┤         │   │
│  │  │ id           │ id           │ id                       │         │   │
│  │  │ name         │ name         │ job_id                   │         │   │
│  │  │ host         │ entity       │ status                   │         │   │
│  │  │ port         │ sql          │ rows_extracted           │         │   │
│  │  │ database     │ engine_type  │ rows_loaded              │         │   │
│  │  │ username     │ source_conn  │ start_time               │         │   │
│  │  │ password 🔒  │ target_conn  │ end_time                 │         │   │
│  │  │ is_valid     │ schedule     │ error_message            │         │   │
│  │  │ tested_at    │ is_active    │ duration                 │         │   │
│  │  └──────────────┴──────────────┴──────────────────────────┘         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                   ↓
                                   ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CAMADA CORE (ETL)                                    │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                  FACTORY PATTERN (Conexões)                           │  │
│  │                                                                       │  │
│  │   ConnectionFactory.create_connection(config)                         │  │
│  │           ↓                                                           │  │
│  │   ┌───────┴─────────┬──────────────┬─────────────┬──────────────┐    │  │
│  │   ↓                 ↓              ↓             ↓              ↓    │  │
│  │ MySQL          PostgreSQL       MSSQL          Oracle          ...   │  │
│  │ (pymysql)      (psycopg2)     (pyodbc)      (cx_Oracle)        │  │  │
│  │                                                                       │  │
│  │   Métodos comuns:                                                     │  │
│  │   • connect() / disconnect()                                          │  │
│  │   • test_connection()                                                 │  │
│  │   • fetch_all() / fetch_one()                                         │  │
│  │   • execute_command() (INSERT/UPDATE/DELETE)                          │  │
│  │   • get_table_columns()                                               │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                  STRATEGY PATTERN (Engines)                           │  │
│  │                                                                       │  │
│  │   ProcessingEngine (Abstrato)                                         │  │
│  │           ↓                                                           │  │
│  │   ┌───────┴────────────────┬──────────────────────────────────┐      │  │
│  │   ↓                        ↓                                  ↓      │  │
│  │ PandasEngine         SparkEngine                   FuturoEngine      │  │
│  │ (em memória)         (distribuído)                  (Polars, etc)   │  │
│  │                                                                       │  │
│  │   Métodos comuns:                                                     │  │
│  │   • read_data(sql)                                                    │  │
│  │   • write_data(df, table)                                             │  │
│  │   • filter / transform / join / group_by / aggregate                  │  │
│  │   • count / show / get_schema                                         │  │
│  │                                                                       │  │
│  │   📊 Escolha automática:                                              │  │
│  │   • < 1GB de dados → Pandas (mais rápido)                             │  │
│  │   • > 1GB de dados → Spark (distribuído)                              │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   ↓
                                   ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CAMADA DE VALIDAÇÃO                                    │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    PYDANTIC SCHEMAS                                   │  │
│  │                                                                       │  │
│  │   BRBaseSchema (Base)                                                 │  │
│  │   ├─ validate_cpf()                                                   │  │
│  │   ├─ validate_cnpj()                                                  │  │
│  │   ├─ validate_cep()                                                   │  │
│  │   ├─ validate_ncm()                                                   │  │
│  │   ├─ validate_email()                                                 │  │
│  │   └─ normalize_string()                                               │  │
│  │                                                                       │  │
│  │   ↓                                                                   │  │
│  │                                                                       │  │
│  │   Schemas Específicos:                                                │  │
│  │   ┌─────────────┬─────────────┬────────────┬──────────────┐          │  │
│  │   │  Produto    │   Cliente   │Fornecedor  │   Vendas     │          │  │
│  │   │             │             │            │              │          │  │
│  │   │ • id        │ • id        │ • id       │ • id         │          │  │
│  │   │ • desc      │ • cnpj_cpf  │ • razao    │ • cliente_id │          │  │
│  │   │ • preco ✓   │ • email ✓   │ • endereco │ • data       │          │  │
│  │   │ • ncm ✓     │ • telefone  │ • cidade   │ • total      │          │  │
│  │   │ • icms ✓    │ • limite    │ • contato  │ • itens      │          │  │
│  │   │ • estoque   │ • ativo     │ • ativo    │ • desconto   │          │  │
│  │   └─────────────┴─────────────┴────────────┴──────────────┘          │  │
│  │                                                                       │  │
│  │   Validações automáticas:                                             │  │
│  │   ✓ Tipos (int, Decimal, str)                                         │  │
│  │   ✓ Ranges (preco > 0, estoque >= 0)                                  │  │
│  │   ✓ Formato (CPF/CNPJ/CEP/Email/NCM)                                  │  │
│  │   ✓ Lógica (estoque <= máximo)                                        │  │
│  │   ✓ Transformação (normalização)                                      │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   ↓
                                   ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CAMADA DE UTILIDADES                                     │
│                                                                             │
│  ┌──────────────┬──────────────┬──────────────────┬──────────────────┐    │
│  │ logger.py    │exceptions.py │ helpers.py       │ decorators.py    │    │
│  │              │              │                  │                  │    │
│  │• Colorizado  │• Domain      │• sanitize_sql()  │• cache           │    │
│  │• Arquivo     │  Exceptions  │• format_bytes()  │• retry           │    │
│  │• Níveis      │• ETL-aware   │• format_duration │• validate        │    │
│  │  (DEBUG...)  │  messages    │• flatten_dict()  │                  │    │
│  └──────────────┴──────────────┴──────────────────┴──────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   ↓
                                   ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                     BANCOS DE DADOS (Origem & Destino)                      │
│                                                                             │
│  ORIGEM (Variável)              DESTINO (Sistema BR)                        │
│  ┌────────────────────┐         ┌────────────────────┐                     │
│  │  Qualquer BD       │         │   PostgreSQL       │                     │
│  │                    │         │  (ou SQL Server)   │                     │
│  │ • MySQL            │         │                    │                     │
│  │ • PostgreSQL       │         │  Tabelas:          │                     │
│  │ • SQL Server       │         │  • produto         │                     │
│  │ • Oracle           │         │  • cliente         │                     │
│  │ • MongoDB (future) │         │  • fornecedor      │                     │
│  │                    │         │  • vendas          │                     │
│  │ Dados brutos,      │         │  • itens_venda     │                     │
│  │ estruturas         │         │  • contas_receber  │                     │
│  │ variadas           │         │  • contas_pagar    │                     │
│  │                    │         │                    │                     │
│  │ Via SQL:           │         │ Via SQL (INSERT):  │                     │
│  │ SELECT ...         │         │ INSERT INTO ...    │                     │
│  │ FROM origem_table  │  ════>  │ VALUES (...)       │                     │
│  └────────────────────┘         └────────────────────┘                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


╔══════════════════════════════════════════════════════════════════════════════╗
║                           FLUXO DE DADOS                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│ Usuário acessa Interface                                                    │
│ Streamlit (http://localhost:8501)                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1️⃣  CADASTRO DE CONEXÃO                                                     │
│                                                                             │
│ ui/pages/connections.py                                                    │
│ ├─ Form recebe dados (host, porta, credenciais)                            │
│ ├─ Factory cria conexão do tipo correto                                    │
│ ├─ Testa conexão (SQL: SELECT 1)                                           │
│ ├─ Criptografa senha com Fernet                                            │
│ └─ Salva em PostgreSQL (db/models/connections.py)                          │
└─────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2️⃣  CRIAR JOB                                                               │
│                                                                             │
│ ui/pages/jobs.py                                                           │
│ ├─ Seleciona conexão de origem e destino                                   │
│ ├─ Define query SQL de extração                                            │
│ ├─ Escolhe engine (Pandas para <1GB, Spark para >1GB)                      │
│ ├─ Configura transformações (opcionais)                                    │
│ └─ Salva em PostgreSQL (db/models/connections.py)                          │
└─────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3️⃣  EXECUTAR JOB                                                            │
│                                                                             │
│ Pipeline ETL Interna                                                       │
│                                                                             │
│ Passo 1: EXTRACT (Extração)                                                 │
│ ├─ Recupera Connection do PostgreSQL                                       │
│ ├─ Descriptografa senha                                                    │
│ ├─ ConnectionFactory.create_connection() → Objeto da DB correta             │
│ ├─ Execute: connection.fetch_all(query)                                    │
│ └─ Resultado: DataFrame (Pandas) ou Resilient Distributed Dataset (Spark)  │
│                                                                             │
│ Passo 2: TRANSFORM (Transformação)                                          │
│ ├─ Engine aplica transformações configuradas                               │
│ ├─ Filtros, joins, agregações, etc                                         │
│ └─ Resultado: Dados transformados                                          │
│                                                                             │
│ Passo 3: VALIDATE (Validação)                                               │
│ ├─ Para cada linha: ProdutoSchema(row)                                     │
│ ├─ Pydantic valida tipos, formatos, ranges                                 │
│ ├─ Se inválido: log de erro, linha rejeitada                               │
│ └─ Resultado: Dados validados                                              │
│                                                                             │
│ Passo 4: LOAD (Carregamento)                                                │
│ ├─ Engine.write_data(df, table_destino)                                    │
│ ├─ INSERT INTO tabela_destino SELECT ...                                   │
│ └─ Resultado: Dados em PostgreSQL destino                                  │
│                                                                             │
│ Passo 5: MONITOR (Monitoramento)                                            │
│ ├─ Salva resultado em ExecutionModel                                       │
│ ├─ Registra: rows_extracted, rows_loaded, duration, status                 │
│ └─ Resultado: Histórico em PostgreSQL                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4️⃣  MONITORAR RESULTADO                                                     │
│                                                                             │
│ ui/pages/monitoramento.py                                                  │
│ ├─ Query ExecutionModel do PostgreSQL                                      │
│ ├─ Exibe: Status, linhas, tempo, erros                                     │
│ ├─ Gráficos de performance                                                 │
│ └─ Alertas automáticos                                                     │
└─────────────────────────────────────────────────────────────────────────────┘


╔══════════════════════════════════════════════════════════════════════════════╗
║                      INTERAÇÕES ENTRE CAMADAS                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

ui/ (Streamlit)
    ├─ lê/escreve em db/ via SQLAlchemy
    └─ chama core/ para processar dados
    
core/connections/
    ├─ Factory cria instâncias de DB connections
    ├─ cada DB implementa interface comum
    └─ devolvem dados para engines processar

core/engines/
    ├─ recebem dados de connections
    ├─ processam (Pandas ou Spark)
    ├─ devolvem DataFrames
    └─ engines não conhecem BD específico

models/schemas/
    ├─ validam dados antes de carregar
    ├─ independentes de engine ou BD
    ├─ reutilizáveis em qualquer contexto
    └─ garantem qualidade de dados

db/ (PostgreSQL)
    ├─ armazena configurações (Connections, Jobs)
    ├─ armazena histórico (Executions)
    └─ audit trail de tudo que passou

utils/
    └─ suporta todas as camadas com logging, exceções, helpers


═══════════════════════════════════════════════════════════════════════════════
Desperta padrões SOLID:
  ✓ S: Cada classe tem uma responsabilidade
  ✓ O: Aberto para extensão (novos engines, BD)
  ✓ L: Engines são intercambiáveis
  ✓ I: Interfaces específicas (read, write, filter, ...)
  ✓ D: Depende de abstrações, não implementações

═══════════════════════════════════════════════════════════════════════════════
'''

print(ARQUITETURA)

if __name__ == "__main__":
    with open("ARQUITETURA.txt", "w", encoding="utf-8") as f:
        f.write(ARQUITETURA)
    print("\n✅ Arquitetura salva em ARQUITETURA.txt")
