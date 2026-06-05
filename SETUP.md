"""
Guia de Instalação e Setup do Sistema ETL

## 1. Pré-requisitos

- Python 3.10+
- PostgreSQL 12+ (para metadados)
- Docker e Docker Compose (opcional)

## 2. Instalação

### 2.1 Clonar/Copiar o projeto
```bash
cd /Users/home/VR/novo_implantacao/sistema_etl
```

### 2.2 Criar ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\\Scripts\\activate  # Windows
```

### 2.3 Instalar dependências
```bash
pip install -r requirements.txt
```

### 2.4 Configurar banco de dados (PostgreSQL)

#### Opção A: Usando Docker Compose (RECOMENDADO)
```bash
docker-compose up -d
```

Aguarde a inicialização (cerca de 10 segundos).

#### Opção B: PostgreSQL Local
```sql
CREATE USER etl_user WITH PASSWORD 'etl_password';
CREATE DATABASE etl_metadata OWNER etl_user;
GRANT ALL PRIVILEGES ON DATABASE etl_metadata TO etl_user;
```

### 2.5 Configurar variáveis de ambiente
```bash
cp .env.example .env
# Editar .env com suas configurações
```

Se usando criptografia, gerar chave:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## 3. Executar a Aplicação

### 3.1 Interface Streamlit (Frontend)
```bash
streamlit run main.py
```

A aplicação abrirá em: http://localhost:8501

### 3.2 Exemplos de Uso
```bash
python exemplo_uso.py
```

## 4. Estrutura do Projeto

```
sistema_etl/
├── config/              # Configurações globais
├── core/                # Núcleo ETL
│   ├── connections/     # Factory Pattern - Conexões DB
│   └── engines/         # Strategy Pattern - Pandas/Spark
├── db/                  # Modelos SQLAlchemy
├── models/              # Schemas Pydantic
├── ui/                  # Interface Streamlit
├── utils/               # Utilitários e helpers
├── tests/               # Testes unitários
└── main.py             # Ponto de entrada Streamlit
```

## 5. Padrões de Projeto Utilizados

### Factory Pattern (Conexões)
Permite criar dinamicamente diferentes tipos de conexões (MySQL, PostgreSQL, MSSQL, Oracle)
sem acoplamento direto.

**Uso:**
```python
from core.connections.factory import ConnectionFactory
from core.connections.base import ConnectionConfig

config = ConnectionConfig(
    host='localhost',
    port=3306,
    database='meu_banco',
    username='usuario',
    password='senha',
    connection_type='mysql'
)

connection = ConnectionFactory.create_connection(config)
```

### Strategy Pattern (Engines)
Abstrai motores de processamento (Pandas vs PySpark), permitindo trocar estratégias
sem alterar lógica de negócio.

**Uso:**
```python
from core.engines.pandas_engine import PandasEngine
from core.engines.spark_engine import SparkEngine

# Usar Pandas
engine = PandasEngine(connection)
df = engine.read_data(query)

# Trocar para Spark - apenas mude a classe
engine = SparkEngine(connection)
spark_df = engine.read_data(query)
```

### Pydantic para Validação
Define schemas tipados que validam dados automaticamente.

**Uso:**
```python
from models.schemas.produto import ProdutoSchema

produto = ProdutoSchema(
    id=1,
    descricaocompleta='Arroz Integral 5kg',
    unidade='KG',
    precovenda=25.50,
    ativo=True
)
# Automáticamente valida NCM, CPF, CNPJ, etc
```

## 6. Fluxo de Uso Típico

1. **Cadastrar Conexão** (UI)
   - Ir em \"Conexões\"
   - Clicar em \"Nova Conexão\"
   - Preencher dados
   - Testar conexão

2. **Criar Job** (UI)
   - Ir em \"Jobs\"
   - Configurar extração SQL
   - Escolher engine (Pandas/Spark)
   - Configurar transformações

3. **Executar Job** (UI)
   - Ir em \"Execuções\"
   - Selecionar job
   - Clicar em executar
   - Monitorar resultado

## 7. Troubleshooting

### Erro de conexão PostgreSQL
```
postgresql://etl_user@localhost/etl_metadata
```
Verificar credenciais em `.env`

### PySpark não funciona
Requer Java instalado:
```bash
# macOS
brew install openjdk

# Linux
apt-get install openjdk-11-jdk

# Verificar
java -version
```

### Streamlit não inicia
```bash
# Limpar cache
rm -rf ~/.streamlit/

# Rodar com debug
streamlit run main.py --logger.level=debug
```

## 8. Próximos Passos

- [ ] Implementar Pipeline abstrata
- [ ] Criar repositórios para persistência
- [ ] Implementar scheduler de jobs
- [ ] Adicionar mais tipos de validação
- [ ] Criar testes unitários completos
- [ ] Documentação de API
- [ ] Deploy em produção

## 9. Contato e Suporte

Sistema desenvolvido como ETL genérico para supermercados.
Baseado em Python, Pandas, PySpark, Pydantic e Streamlit.
"""

# Imprimir este arquivo para leitura
if __name__ == "__main__":
    import sys
    with open(__file__) as f:
        print(f.read())
