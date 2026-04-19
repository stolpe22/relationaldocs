---
paths:
  - "backend/src/api/**/*.py"
---
# Regras da API (api/)

- Framework: FastAPI. Router por recurso em `routers/`.
- Schemas de request/response em `schemas/` como Pydantic `BaseModel` com `model_config = ConfigDict(strict=True)`.
- Toda rota deve ter `response_model` explícito, `summary` e `tags`.
- Erros retornam JSON padronizado: `{"detail": "mensagem", "error_code": "CODIGO"}`.
- Use `HTTPException` com códigos corretos: 400, 404, 500, 422.
- Injeção de dependência via `Depends()` — services e readers injetados, nunca instanciados na rota.
- Rotas não contêm lógica de negócio — delegam para services.
- O schema de conexão (`ConnectionRequest`) deve ter campo `db_type: Literal["oracle"]` agora, mas modelado como `str` com validação contra `SUPPORTED_DATABASES` para escalar sem breaking change quando novos bancos forem adicionados.

## Autenticação
- Todas as rotas (exceto `GET /health`) protegidas por API key via header `X-API-Key`.
- Chave lida de variável de ambiente `API_KEY`. Se ausente ou inválida → 401 com `error_code: "UNAUTHORIZED"`.
- Implementar como `Depends(verify_api_key)` em `src/api/dependencies.py`.

## CORS
- `allow_origins` deve ser lido de variável de ambiente `CORS_ORIGINS` (lista separada por vírgula).
- Em dev aceita `["*"]` somente se `ENV=development`. Em produção exige lista explícita — falha no startup se `CORS_ORIGINS` não estiver definido.

## Lifecycle e cleanup
- Usar `@asynccontextmanager` no `lifespan` do FastAPI para startup/shutdown.
- No shutdown: fechar túnel SSH ativo (se houver) e conexão de pool Oracle.
- Nunca deixar recursos abertos ao encerrar o processo.

## Operações longas (generate)
- `POST /api/v1/generate` dispara `BackgroundTasks` e retorna imediatamente `{"job_id": "uuid"}` com status 202.
- `GET /api/v1/jobs/{job_id}` retorna `{"status": "pending|running|done|error", "result_url": "..."|null}`.
- Quando done, resultado disponível em `GET /api/v1/jobs/{job_id}/download` como ZIP.
- Jobs expiram após 10 minutos — arquivo ZIP e estado removidos do disco.

## Endpoints completos
  - `GET  /health` — healthcheck (sem auth), retorna `{"status": "ok"}`
  - `POST /api/v1/connections/test` — testa conexão com o banco
  - `POST /api/v1/tunnels/open` — abre túnel SSH
  - `POST /api/v1/tunnels/close` — fecha túnel SSH
  - `GET  /api/v1/tunnels/status` — retorna estado atual do túnel: `{"active": bool, "local_port": int|null}`
  - `GET  /api/v1/schemas` — lista schemas disponíveis no banco conectado
  - `GET  /api/v1/tables?schema=X&limit=100&offset=0` — lista tabelas com paginação obrigatória
  - `POST /api/v1/analysis` — retorna dashboard analítico das tabelas selecionadas
  - `POST /api/v1/generate` — dispara geração async, retorna job_id (202)
  - `GET  /api/v1/jobs/{job_id}` — polling de status do job
  - `GET  /api/v1/jobs/{job_id}/download` — download do ZIP quando job concluído