---
paths:
  - "backend/tests/**/*.py"
---
# Regras de Testes

- Framework: pytest. Plugins permitidos: pytest-cov, pytest-asyncio, pytest-mock.
- Nomenclatura: `test_{metodo}_{cenario}_{resultado_esperado}` — ex: `test_fetch_metadata_empty_tables_raises_metadata_error`.
- Um arquivo de teste por módulo: `tests/unit/test_markdown_service.py` para `src/services/markdown_service.py`.
- Fixtures reutilizáveis em `conftest.py` — nunca duplicar setup entre testes.
- Mocks para dependências externas (banco, SSH). Nunca mockar a classe sob teste.
- Testes de integração marcados com `@pytest.mark.integration` — não rodam por padrão.
- Cada teste deve ter exatamente um assert principal (asserts auxiliares de setup são OK).
- Cobertura mínima alvo: 80% em `src/core/` e `src/services/`.
- Fixtures de exemplo de metadados Oracle (Table, Column, Constraint, Trigger) devem existir em `conftest.py`.

## Testes de integração
- Usar imagem Docker `gvenzl/oracle-xe:21-slim` para testes `@pytest.mark.integration`.
- `docker-compose.test.yml` na raiz com serviço `oracle-test` — porta 1521, usuário/senha fixos para CI.
- Testes de integração NÃO rodam por padrão. Ativar com `pytest -m integration`.
- Pipeline CI deve subir o container antes de rodar a suite de integração.