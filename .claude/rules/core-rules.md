---
paths:
  - "backend/src/core/**/*.py"
---
# Regras do Domínio (core/)

- Nunca importe de `src/adapters/` ou `src/api/` dentro de `backend/` — core é a camada mais interna, sem dependências externas.
- Toda entidade de domínio (Table, Column, Constraint, Trigger) deve ser `@dataclass(frozen=True)`.
- Interfaces (ABCs) devem ter apenas métodos abstratos, sem implementação.
- `DatabaseReader` deve expor: `connect()`, `disconnect()`, `fetch_metadata(schema: str, tables: list[str]) -> list[Table]`.
- `MarkdownRenderer` deve expor: `render(table: Table) -> str`.
- `TunnelManager` deve expor: `open()`, `close()`, `local_bind_port: int`.
- Exceptions devem herdar de `RelationalsDocError` (base), nunca de `Exception` diretamente.
- Exceptions tipadas: `ConnectionError`, `MetadataError`, `RenderError`, `TunnelError`.
- Tudo em core deve ter 100% de type hints, sem `Any`.