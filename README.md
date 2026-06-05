# Sistema ETL Genérico para Supermercados

Um sistema ETL (Extract-Transform-Load) modular, escalável e de fácil manutenção para integração de dados de supermercados.

## 📁 Estrutura do Projeto

```
sistema_etl/
│
├── config/                          # Configurações da aplicação
│   ├── __init__.py
│   ├── settings.py                  # Variáveis de ambiente e configurações globais
│   └── constants.py                 # Constantes do sistema
│
├── core/                            # Núcleo do sistema ETL
│   ├── __init__.py
│   │
│   ├── connections/                 # Factory Pattern - Gestão de Conexões
│   │   ├── __init__.py
│   │   ├── base.py                  # Interface abstrata para conexões
│   │   ├── factory.py               # Factory para instanciar conexões
│   │   ├── mysql.py                 # Implementação MySQL
│   │   ├── mssql.py                 # Implementação SQL Server
│   │   ├── postgresql.py            # Implementação PostgreSQL
│   │   └── oracle.py                # Implementação Oracle
│   │
│   ├── engines/                     # Strategy Pattern - Motores de Processamento
│   │   ├── __init__.py
│   │   ├── base.py                  # Interface abstrata para engines
│   │   ├── pandas_engine.py         # Implementação Pandas
│   │   └── spark_engine.py          # Implementação PySpark
│   │
│   └── pipelines/                   # Orquestração do ETL
│       ├── __init__.py
│       ├── base.py                  # Pipeline abstrato
│       └── etl_pipeline.py          # Pipeline principal
│
├── db/                              # Persistência de Metadados (PostgreSQL)
│   ├── __init__.py
│   ├── base.py                      # Configuração SQLAlchemy
│   │
│   ├── models/                      # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── connections.py           # Modelo de Conexões
│   │   └── jobs.py                  # Modelo de Tarefas (Jobs)
│   │
│   └── repositories/                # Data Access Layer
│       ├── __init__.py
│       ├── connection_repo.py       # Repositório de Conexões
│       └── job_repo.py              # Repositório de Jobs
│
├── models/                          # Modelos de Dados (Pydantic)
│   ├── __init__.py
│   │
│   ├── schemas/                     # Schemas Pydantic do Sistema BR
│   │   ├── __init__.py
│   │   ├── base.py                  # Schema base com validações comuns
│   │   ├── produto.py               # Schema para Produtos
│   │   ├── cliente.py               # Schema para Clientes
│   │   ├── fornecedor.py            # Schema para Fornecedores
│   │   ├── vendas.py                # Schema para Vendas
│   │   ├── itens_venda.py           # Schema para Itens de Venda
│   │   ├── contas_receber.py        # Schema para Contas a Receber
│   │   └── contas_pagar.py          # Schema para Contas a Pagar
│   │
│   └── validators/                  # Validadores customizados
│       ├── __init__.py
│       └── field_validators.py      # Validadores de campos específicos
│
├── ui/                              # Interface Streamlit
│   ├── __init__.py
│   ├── app.py                       # Aplicação principal
│   │
│   └── pages/                       # Páginas da aplicação
│       ├── __init__.py
│       ├── home.py                  # Dashboard principal
│       ├── connections.py           # Gestão de conexões
│       ├── jobs.py                  # Gestão de tarefas
│       ├── execucoes.py             # Histórico de execuções
│       └── monitoramento.py         # Monitoramento e logs
│
├── utils/                           # Utilitários
│   ├── __init__.py
│   ├── logger.py                    # Sistema de logging
│   ├── exceptions.py                # Exceções customizadas
│   ├── decorators.py                # Decoradores úteis
│   └── helpers.py                   # Funções auxiliares
│
├── tests/                           # Testes Unitários
│   ├── __init__.py
│   ├── test_connections.py
│   ├── test_engines.py
│   ├── test_schemas.py
│   └── test_pipelines.py
│
├── requirements.txt                 # Dependências do projeto
├── .env.example                     # Exemplo de variáveis de ambiente
├── docker-compose.yml               # Compose para PostgreSQL de metadata
└── main.py                          # Ponto de entrada da aplicação
```

## 🏗️ Padrões de Projeto

### 1. **Factory Pattern** (Conexões)
Permite instanciar dinamicamente diferentes tipos de conexões de banco de dados sem acoplamento.

### 2. **Strategy Pattern** (Engines)
Abstrai os motores de processamento (Pandas vs PySpark), permitindo trocar estratégias sem alterar lógica de negócio.

### 3. **Repository Pattern** (Persistência)
Centraliza acesso aos dados de metadados, facilitando testes e manutenção.

## 🛠️ Tecnologias

- **Python 3.10+**
- **Pandas** - Processamento de dados em memória
- **PySpark** - Processamento distribuído de grandes volumes
- **Pydantic** - Validação e serialização de dados
- **SQLAlchemy** - ORM para PostgreSQL
- **Streamlit** - Interface web
- **PostgreSQL** - Persistência de metadados
- **pytest** - Testes unitários

## 📋 Como Usar

Ver seções abaixo para detalhes de cada componente.
# novo_implantacao
