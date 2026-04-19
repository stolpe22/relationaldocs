import io
import zipfile
from collections import defaultdict

from core.models.constraint import Constraint
from core.models.table import Table

# column_name → [related_tables]
ImplicitMap = dict[str, list[str]]


class MarkdownService:
    """Renderiza tabelas Oracle para markdown Obsidian-compatible e empacota em ZIP."""

    def generate_zip(
        self,
        schema: str,
        tables: list[Table],
        implicit: dict[str, ImplicitMap] | None = None,
    ) -> bytes:
        implicit = implicit or {}
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for table in tables:
                zf.writestr(
                    f"{table.name}.md",
                    self.render(table, implicit.get(table.name, {})),
                )
        return buf.getvalue()

    def render(self, table: Table, implicit: ImplicitMap | None = None) -> str:  # noqa: C901
        implicit = implicit or {}
        lines: list[str] = []

        # Mapa coluna → constraints que a incluem
        col_constraints: dict[str, list[Constraint]] = defaultdict(list)
        for con in table.constraints:
            for col_name in con.columns:
                col_constraints[col_name].append(con)

        pk_columns = {
            col_name
            for con in table.constraints if con.type == "PK"
            for col_name in con.columns
        }
        fk_columns = {
            col_name
            for con in table.constraints if con.type == "FK"
            for col_name in con.columns
        }

        implicit_count = len(implicit)

        # ── Front matter ─────────────────────────────────────────────────────
        lines += [
            "---",
            f"tags: [tabela, {table.schema.lower()}, winthor]",
            f"schema: {table.schema}",
            f"tabela: {table.name}",
            f"colunas: {len(table.columns)}",
            f"triggers: {len(table.triggers)}",
            f"constraints: {len(table.constraints)}",
            f"relacionamentos_implicitos: {implicit_count}",
            "---",
            "",
        ]

        # ── Título e comentário ───────────────────────────────────────────────
        lines.append(f"# {table.name}")
        if table.comment and table.comment.strip():
            lines += ["", f"> {table.comment.strip()}", ""]

        lines += ["---", ""]

        # ── Colunas ──────────────────────────────────────────────────────────
        lines += ["## Colunas", ""]

        for col in sorted(table.columns, key=lambda c: c.order):
            col_implicit = implicit.get(col.name, [])

            badges = ""
            if col.name in pk_columns:
                badges += " 🔑"
            if col.name in fk_columns:
                badges += " 🔗"
            if col_implicit:
                badges += " 🤝"
            if not col.nullable:
                badges += " 🔒 Obrigatório"

            lines.append(f"### {col.name}{badges}")
            lines.append(f"- **Ordem:** {col.order}")
            lines.append(f"- **Tipo:** `{col.data_type}`")
            lines.append(f"- **Tamanho:** {col.length if col.length else '—'}")
            lines.append(f"- **Precisão:** {col.precision if col.precision is not None else '—'}")
            lines.append(f"- **Escala:** {col.scale if col.scale is not None else '—'}")
            lines.append(f"- **Nulo:** {'Sim' if col.nullable else 'Não'}")
            lines.append(f"- **Default:** {col.default.strip() if col.default else '—'}")
            lines.append(f"- **Comentário:** {col.comment.strip() if col.comment else '—'}")

            for con in col_constraints.get(col.name, []):
                if con.type == "PK":
                    lines.append(f"- **Constraint:** `{con.name}` (P — Primary Key)")
                elif con.type == "FK":
                    try:
                        idx = list(con.columns).index(col.name)
                        ref_col = (
                            con.ref_columns[idx]
                            if con.ref_columns and idx < len(con.ref_columns)
                            else "?"
                        )
                    except ValueError:
                        ref_col = "?"
                    ref_table = con.ref_table or "?"
                    lines.append(f"- **Constraint:** `{con.name}` (R — Foreign Key)")
                    lines.append(f"- 🔗 Referencia coluna `{ref_col}` em [[{ref_table}]]")
                elif con.type == "UK":
                    lines.append(f"- **Constraint:** `{con.name}` (U — Unique)")
                elif con.type == "CHECK":
                    cond = f" → `{con.search_condition}`" if con.search_condition else ""
                    lines.append(f"- **Constraint:** `{con.name}` (C — Check){cond}")

            if col_implicit:
                links = ", ".join(f"[[{t}]]" for t in sorted(col_implicit))
                lines.append(f"- **Relacionamento Implícito:** `{col.name}` — vínculo sugerido com {links}")

            lines += ["", "---", ""]

        # ── Constraints ───────────────────────────────────────────────────────
        pks = [c for c in table.constraints if c.type == "PK"]
        fks = [c for c in table.constraints if c.type == "FK"]
        checks = [c for c in table.constraints if c.type == "CHECK"]
        uks = [c for c in table.constraints if c.type == "UK"]

        if table.constraints:
            lines += ["## Constraints", ""]

            if pks:
                lines.append("### 🔑 Primary Key (P)")
                for con in pks:
                    cols = "`, `".join(con.columns)
                    lines.append(f"- **{con.name}** → `{cols}`")
                lines.append("")

            if fks:
                lines.append("### 🔗 Foreign Key (R)")
                for con in fks:
                    src = "`, `".join(con.columns)
                    ref_table = con.ref_table or "?"
                    ref_cols = ", ".join(f"`{c}`" for c in (con.ref_columns or []))
                    lines.append(
                        f"- **{con.name}** → `{src}` referencia {ref_cols} em [[{ref_table}]]"
                    )
                lines.append("")

            if checks:
                lines.append("### ✅ Check (C)")
                for con in checks:
                    cond = f" → `{con.search_condition}`" if con.search_condition else ""
                    cols = "`, `".join(con.columns)
                    lines.append(f"- **{con.name}** → `{cols}`{cond}")
                lines.append("")

            if uks:
                lines.append("### 🔒 Unique (U)")
                for con in uks:
                    cols = "`, `".join(con.columns)
                    lines.append(f"- **{con.name}** → `{cols}`")
                lines.append("")

            lines += ["---", ""]

        # ── Triggers ──────────────────────────────────────────────────────────
        if table.triggers:
            lines += ["## Triggers", ""]
            for trg in table.triggers:
                lines.append(f"- **{trg.name}** — `{trg.trigger_type}` → `{trg.event}`")
            lines += ["", "---", ""]

        # ── Relacionamentos ───────────────────────────────────────────────────
        fk_targets = sorted({con.ref_table for con in fks if con.ref_table})
        # implícitos: coluna → tabelas; invertemos para tabela → colunas
        implicit_by_table: dict[str, list[str]] = defaultdict(list)
        for col_name, rel_tables in implicit.items():
            for rel_table in rel_tables:
                implicit_by_table[rel_table].append(col_name)

        if fk_targets or implicit_by_table:
            lines += ["## Relacionamentos", ""]

            if fk_targets:
                lines.append("### 🔗 Explícitos (Foreign Keys)")
                lines.append("Tabelas referenciadas fisicamente por Constraints desta tabela:")
                lines.append("")
                for con in fks:
                    ref_table = con.ref_table or "?"
                    src = ", ".join(f"`{c}`" for c in con.columns)
                    ref = ", ".join(f"`{c}`" for c in (con.ref_columns or []))
                    ref_str = f" → {ref}" if ref else ""
                    lines.append(f"- [[{ref_table}]] — coluna {src}{ref_str}")
                lines.append("")

            if implicit_by_table:
                lines.append("### 🤝 Implícitos (Metadados WinThor)")
                lines.append(
                    "Vínculos inferidos pela nomenclatura de colunas chave (COD%, NUM%):"
                )
                lines.append("")
                for rel_table, cols in sorted(implicit_by_table.items()):
                    col_list = ", ".join(f"`{c}`" for c in sorted(cols))
                    lines.append(f"- [[{rel_table}]] — via coluna {col_list}")
                lines.append("")

        return "\n".join(lines)
