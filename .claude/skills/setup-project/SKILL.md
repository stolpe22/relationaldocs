---
name: setup-project
description: Bootstrap completo do projeto — cria estrutura de pastas e arquivos base (apenas adapter Oracle).
disable-model-invocation: true
allowed-tools: Bash, Write, Read
---
Inicialize o projeto Relationals Doc do zero.

1. Crie a árvore de diretórios:
```bash
mkdir -p backend/src/{core/{models,interfaces},adapters/oracle,services,api/{routers,schemas}}
mkdir -p backend/tests/{unit,integration}
mkdir -p backend/output
```
NÃO crie pastas para postgres, sqlserver ou mysql. Apenas oracle.
O frontend fica em `frontend/` na raiz — separado do backend. Nenhum código Python vai em `frontend/`.

Para o frontend, rode:
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend && npm install
npm install tailwindcss @tailwindcss/vite
```
Estrutura esperada em `frontend/src/`: `api/client.ts`, `context/AppContext.tsx`, `components/`, `hooks/`.

Configure Tailwind v4:
- Em `vite.config.ts`: adicione `import tailwindcss from '@tailwindcss/vite'` e inclua `tailwindcss()` no array `plugins`.
- Em `src/index.css`: substitua o conteúdo por `@import "tailwindcss";` seguido do bloco `@theme` com as cores do projeto.
- **Nunca crie arquivos `.module.css`** — toda estilização via classes Tailwind diretamente nos componentes.

2. Crie `backend/pyproject.toml` com:
- Dependências: fastapi, uvicorn[standard], oracledb, paramiko, pydantic, python-dotenv
- Dev: pytest, pytest-cov, pytest-asyncio, pytest-mock, ruff, mypy
- Python >=3.11

3. Crie __init__.py em todos os pacotes Python dentro de `backend/src/`.

4. Crie `backend/src/core/exceptions.py` com RelationalsDocError base e filhas: ConnectionError, MetadataError, RenderError, TunnelError.

5. Crie `backend/src/core/interfaces/database_reader.py` com ABC DatabaseReader — métodos genéricos, sem referência a Oracle.

6. Crie `backend/src/core/interfaces/markdown_renderer.py` com ABC MarkdownRenderer.

7. Crie `backend/src/core/interfaces/tunnel_manager.py` com ABC TunnelManager.

8. Crie `backend/src/core/models/table.py`, `column.py`, `constraint.py`, `trigger.py` como dataclasses frozen.

9. Crie `backend/src/adapters/__init__.py` com SUPPORTED_DATABASES registry (oracle ativo, postgres/sqlserver/mysql comentados como futuros) e função get_reader().

10. Crie `backend/src/adapters/oracle/queries.py` com a query de metadados completa (ALL_TAB_COLUMNS + joins) como constante.

11. Crie `backend/src/adapters/oracle/reader.py` com OracleReader(DatabaseReader) implementado para Oracle via oracledb.

12. Crie `backend/src/api/main.py` com:
- App FastAPI com `lifespan` (asynccontextmanager) para startup/shutdown.
- CORS com `allow_origins` lido de `CORS_ORIGINS` (env). Em dev aceita `["*"]` se `ENV=development`.
- Router de health: `GET /health` retorna `{"status": "ok"}` sem autenticação.
- Dependency `verify_api_key` em `backend/src/api/dependencies.py` — lê `API_KEY` do env, retorna 401 se inválida.
- Todos os outros routers incluem `Depends(verify_api_key)`.

13. Crie `backend/.env.example` com: DB_TYPE=oracle, DB_HOST, DB_PORT, DB_SERVICE, DB_USER, DB_PASSWORD, DB_SCHEMA, SSH_HOST, SSH_PORT, SSH_USER, SSH_PASSWORD, API_KEY, CORS_ORIGINS, ENV=development, DB_POOL_ENABLED=false, DB_POOL_MIN=1, DB_POOL_MAX=5, DB_POOL_INCREMENT=1, ORACLE_INSTANT_CLIENT=/opt/oracle/instantclient_21_15.

14. Crie `.gitignore` na raiz com: .venv/, backend/output/, .env, __pycache__/, *.pyc, .mypy_cache/, .pytest_cache/, .ruff_cache/.

15. Crie `backend/tests/conftest.py` com fixtures de exemplo Oracle (Table PCPRODUT com Column, Constraint FK para PCFORNEC, Trigger).

16. Rode `pip install -e ".[dev]"` dentro de `backend/` e `ruff check backend/src` para validar.