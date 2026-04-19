---
paths:
  - "backend/src/adapters/**/*.py"
---
# Regras dos Adapters (adapters/)

## Escopo atual
- APENAS oracle/ existe e deve ser implementado. Não crie pastas para postgres, sqlserver ou mysql agora.
- A skill /skill add-adapter existe para quando for hora de adicionar outro banco — até lá, foco 100% em Oracle.

## Arquitetura (vale para qualquer adapter futuro)
- Cada adapter implementa DatabaseReader de core/interfaces/.
- Um adapter por pasta: oracle/, e futuramente postgres/, sqlserver/, mysql/.
- Cada pasta deve conter: reader.py, queries.py, __init__.py.
- SQL em queries.py como constantes str nomeadas em UPPER_SNAKE: FETCH_METADATA_QUERY, FETCH_TABLES_QUERY.

## Oracle específico
- Driver: oracledb com **thick mode obrigatório** via `oracledb.init_oracle_client()` no topo do módulo reader.py.
- Thick mode é necessário para suportar bancos com password verifier antigo (10g/11g style), comum em bancos 19c migrados.
- Caminho do Instant Client lido de `ORACLE_INSTANT_CLIENT` (env, default `/opt/oracle/instantclient_21_15`).
- O `init_oracle_client` é chamado uma vez no import, dentro de try/except — se já inicializado ou não disponível, cai silenciosamente para thin mode.
- Oracle Instant Client 21.x instalado no container via Dockerfile (ver `.devcontainer/Dockerfile`).
- Parâmetros bind com `:param` (named bind variables Oracle). Nunca f-strings em SQL.
- `connect()` deve validar conexão com `SELECT 1 FROM DUAL` antes de retornar.
- `disconnect()` deve ser idempotente.
- Trate `oracledb.DatabaseError` e re-lance como `core.exceptions.ConnectionError` ou `MetadataError`.
- A query de metadados completa (ALL_TAB_COLUMNS + joins) deve estar em queries.py como `FETCH_METADATA_QUERY`.
- Docstring de OracleReader deve mencionar: "Oracle 11g+. Futuros bancos: PostgreSQL, SQL Server, MySQL via mesmo contrato DatabaseReader."

## Connection Pooling
- OracleReader deve suportar pool via `oracledb.create_pool()` quando configurado.
- Parâmetros de pool lidos de variáveis de ambiente: `DB_POOL_MIN` (default 1), `DB_POOL_MAX` (default 5), `DB_POOL_INCREMENT` (default 1).
- `connect()` adquire conexão do pool; `disconnect()` devolve ao pool (não fecha o pool).
- Pool fechado apenas no shutdown via lifespan do FastAPI.
- Usar pool somente se `DB_POOL_ENABLED=true` — caso contrário manter comportamento simples (conexão direta) para dev local.

## Factory / Registry
- Em src/adapters/__init__.py, manter um dict/registry simples:
- SUPPORTED_DATABASES com "oracle" apontando para src.adapters.oracle.OracleReader
- Futuros adapters (postgres, sqlserver, mysql) ficam apenas como comentário no dict.
- Função get_reader(db_type: str) -> DatabaseReader que instancia pelo registry. Se db_type não existe, raise ValueError com mensagem listando os suportados.