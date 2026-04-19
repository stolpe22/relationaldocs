---
name: add-adapter
description: Cria a estrutura completa de um novo adapter de banco de dados.
allowed-tools: Read, Write, Edit, Glob
---
Crie um novo adapter de banco de dados para: $ARGUMENTS (ex: "postgres", "sqlserver", "mysql").

1. Leia `src/core/interfaces/database_reader.py` para obter a ABC `DatabaseReader`.
2. Leia um adapter existente (ex: `src/adapters/oracle/`) como referência de estrutura.
3. Crie a pasta `src/adapters/{$ARGUMENTS}/` com:
   - `__init__.py` — re-export da classe Reader.
   - `reader.py` — classe `{Name}Reader(DatabaseReader)` com todos os métodos abstratos implementados (stubs com `raise NotImplementedError` onde lógica específica for necessária).
   - `queries.py` — constantes SQL adaptadas para o dialeto do banco (FETCH_METADATA_QUERY, FETCH_TABLES_QUERY) equivalentes ao Oracle mas na sintaxe correta do banco alvo.
4. Adicione import no `src/adapters/__init__.py`.
5. Crie `tests/unit/test_{$ARGUMENTS}_reader.py` com teste base de instanciação e teste de que implementa a interface.
6. Verifique com `ruff check src/adapters/{$ARGUMENTS}/` que não há erros de lint.
7. Liste quais dependências de driver precisam ser adicionadas ao `pyproject.toml` (ex: `psycopg2-binary` para postgres).