---
name: add-endpoint
description: Cria uma rota completa na API com schema, router e injeção de dependência.
allowed-tools: Read, Write, Edit, Glob
---
Crie um novo endpoint na API para: $ARGUMENTS (ex: "POST /analysis - retorna dashboard analítico").

1. Leia `src/api/routers/` e `src/api/schemas/` para entender o padrão existente.
2. Extraia do $ARGUMENTS: método HTTP, path, descrição.
3. Crie ou edite o router correspondente em `src/api/routers/`.
4. Crie schemas de request e response em `src/api/schemas/` como Pydantic BaseModel com `strict=True`.
5. Adicione `response_model`, `summary` e `tags` na decoração da rota.
6. Injete dependências via `Depends()` — nunca instancie services dentro da rota.
7. Trate erros com `HTTPException` e formato padronizado `{"detail": "...", "error_code": "..."}`.
8. Registre o router em `src/api/main.py` se for novo.
9. Crie `tests/unit/test_router_{recurso}.py` com teste da rota usando `TestClient`.
10. Rode `ruff check src/api/` para validar.