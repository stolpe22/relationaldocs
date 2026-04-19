---
paths:
  - "backend/src/services/markdown_service.py"
  - "backend/output/**/*.md"
---
# Regras de Geração Markdown

## Arquivo por tabela
- Cada tabela gera exatamente um arquivo: `{TABLE_NAME}.md` (uppercase, igual ao banco).
- Wikilinks Obsidian para FKs: `[[TABELA_REFERENCIADA]]` — nunca links markdown padrão.
- Seções sem conteúdo são omitidas (sem triggers → sem seção Triggers).

## Estrutura obrigatória

```
---
tags: [tabela, {schema_lower}, winthor]
schema: {SCHEMA}
tabela: {TABLE_NAME}
colunas: {N}
triggers: {N}
constraints: {N}
---

# TABLE_NAME

> TABLE_COMMENT (omitir blockquote se vazio)

---

## Colunas

### COLUNA_PK 🔑 🔒 Obrigatório
- **Ordem:** COLUMN_ID
- **Tipo:** `DATA_TYPE`
- **Tamanho:** DATA_LENGTH (— se nulo)
- **Precisão:** DATA_PRECISION (— se nulo)
- **Escala:** DATA_SCALE (— se nulo)
- **Nulo:** Sim | Não
- **Default:** DATA_DEFAULT (— se nulo)
- **Comentário:** COLUMN_COMMENT (— se vazio)
- **Constraint:** `CONSTRAINT_NAME` (P — Primary Key)
- **Constraint:** `CONSTRAINT_NAME` (R — Foreign Key)
  - 🔗 Referencia coluna `FK_REF_COLUMN` em [[FK_REF_TABLE]]
- **Constraint:** `CONSTRAINT_NAME` (C — Check) → `SEARCH_CONDITION`
- **Constraint:** `CONSTRAINT_NAME` (U — Unique)

---   ← separador após cada coluna

## Constraints

### 🔑 Primary Key (P)
- **CONSTRAINT_NAME** → `COL1`

### 🔗 Foreign Key (R)
- **CONSTRAINT_NAME** → `COL1` referencia `REF_COL` em [[REF_TABLE]]

### ✅ Check (C)
- **CONSTRAINT_NAME** → `COL1` → `SEARCH_CONDITION`

### 🔒 Unique (U)
- **CONSTRAINT_NAME** → `COL1`

---

## Triggers

- **TRIGGER_NAME** — `TRIGGER_TYPE` → `TRIGGERING_EVENT`

---

## Relacionamentos

Tabelas referenciadas por Foreign Keys desta tabela:

- [[FK_REF_TABLE]]
```

## Regras de badges nas colunas
- 🔑 no H3 → somente se a coluna participa de constraint tipo P (PK)
- 🔗 no H3 → somente se a coluna participa de constraint tipo R (FK formal)
- 🤝 no H3 → somente se identificado relacionamento implícito (COD%/NUM%) e NÃO é FK formal
- 🔒 Obrigatório no H3 → somente se NULLABLE = N
- Linha `- **Constraint:**` → só aparece se a coluna tem constraint
- Sub-linha `🔗 Referencia` → só se CONSTRAINT_TYPE = R
- Linha `- **Relacionamento Implícito:**` → só se coluna tem vínculo implícito detectado

## Relacionamentos implícitos
- Detectados por `FETCH_IMPLICIT_RELATIONS_QUERY`: colunas com mesmo nome (COD%, NUM%) e mesmo tipo entre tabelas
- No markdown: seção `### 🤝 Implícitos (Metadados WinThor)` dentro de `## Relacionamentos`
- Formato: `- [[TABELA]] — via coluna \`COLUNA\``
- No front matter: `relacionamentos_implicitos: N` (count de colunas com vínculo na tabela)

## Mapeamento de campos Oracle → documento
| Campo SELECT | Onde aparece |
|---|---|
| TABLE_NAME | H1 + front matter tabela |
| COLUMN_NAME | H3 de cada coluna |
| COLUMN_ID | Campo Ordem |
| DATA_TYPE | Campo Tipo (raw, sem formatação) |
| DATA_LENGTH | Campo Tamanho |
| DATA_PRECISION | Campo Precisão |
| DATA_SCALE | Campo Escala |
| NULLABLE | Campo Nulo + badge 🔒 se N |
| DATA_DEFAULT | Campo Default |
| COLUMN_COMMENT | Campo Comentário |
| TABLE_COMMENT | Blockquote abaixo do H1 |
| CONSTRAINT_NAME | Constraint dentro da coluna + seção Constraints |
| CONSTRAINT_TYPE | P/R/U/C entre parênteses |
| FK_REF_TABLE | Wikilink [[TABELA]] na FK |
| FK_REF_COLUMN | Coluna referenciada ao lado do wikilink |
| SEARCH_CONDITION | Após seta em constraint Check |
| trigger_type | Tipo do trigger (BEFORE EACH ROW etc.) |
| event | Evento do trigger (INSERT OR UPDATE etc.) |
