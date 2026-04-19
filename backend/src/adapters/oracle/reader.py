"""Oracle 11g+. Futuros bancos: PostgreSQL, SQL Server, MySQL via mesmo contrato DatabaseReader."""
import os
from collections import defaultdict
from typing import Any

import oracledb

# Thick mode: necessário para bancos com verifier antigo (10g/11g style) em Oracle 19c+
_INSTANT_CLIENT = os.getenv("ORACLE_INSTANT_CLIENT", "/opt/oracle/instantclient_21_15")
_TNS_ADMIN = os.getenv("TNS_ADMIN", os.path.join(_INSTANT_CLIENT, "network", "admin"))
try:
    oracledb.init_oracle_client(lib_dir=_INSTANT_CLIENT, config_dir=_TNS_ADMIN)
except Exception:
    pass  # já inicializado ou instant client não disponível — usa thin mode

from adapters.oracle.queries import (
    FETCH_CONSTRAINTS_QUERY,
    FETCH_IMPLICIT_RELATIONS_QUERY,
    FETCH_METADATA_QUERY,
    FETCH_SCHEMAS_QUERY,
    FETCH_TABLES_QUERY,
    FETCH_TRIGGERS_QUERY,
)
from core.exceptions import ConnectionError, MetadataError
from core.interfaces.database_reader import DatabaseReader
from core.models.column import Column
from core.models.constraint import Constraint, ConstraintType
from core.models.table import Table
from core.models.trigger import Trigger

_CONSTRAINT_TYPE_MAP: dict[str, ConstraintType] = {
    "P": "PK",
    "R": "FK",
    "U": "UK",
    "C": "CHECK",
}


class OracleReader(DatabaseReader):
    def __init__(
        self,
        host: str,
        port: int,
        service_name: str,
        user: str,
        password: str,
        connection_type: str = "service_name",
    ) -> None:
        self._host = host
        self._port = port
        self._service_name = service_name
        self._user = user
        self._password = password
        self._connection_type = connection_type
        self._connection: oracledb.Connection | None = None

    def _build_dsn(self, enable_broken: bool = True) -> str:
        connect_data = (
            f"(SID={self._service_name})"
            if self._connection_type == "sid"
            else f"(SERVICE_NAME={self._service_name})(SERVER=DEDICATED)"
        )
        if enable_broken:
            return (
                f"(DESCRIPTION=(ENABLE=broken)"
                f"(ADDRESS=(PROTOCOL=TCP)(HOST={self._host})(PORT={self._port}))"
                f"(CONNECT_DATA={connect_data}))"
            )
        else:
            return (
                f"(DESCRIPTION="
                f"(ADDRESS=(PROTOCOL=TCP)(HOST={self._host})(PORT={self._port}))"
                f"(CONNECT_DATA={connect_data}))"
            )

    def connect(self, try_without_broken: bool = True) -> None:
        import logging
        logger = logging.getLogger("oracle.reader")
        try:
            dsn = self._build_dsn(enable_broken=True)
            logger.info(f"Tentando conectar com ENABLE=broken: DSN={dsn}")
            conn = oracledb.connect(user=self._user, password=self._password, dsn=dsn)
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM DUAL")
            self._connection = conn
        except oracledb.DatabaseError as exc:
            logger.error(f"Erro ao conectar com ENABLE=broken: {exc}")
            if try_without_broken:
                try:
                    dsn2 = self._build_dsn(enable_broken=False)
                    logger.info(f"Tentando conectar sem ENABLE=broken: DSN={dsn2}")
                    conn = oracledb.connect(user=self._user, password=self._password, dsn=dsn2)
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1 FROM DUAL")
                    self._connection = conn
                    return
                except oracledb.DatabaseError as exc2:
                    logger.error(f"Erro ao conectar sem ENABLE=broken: {exc2}")
                    raise ConnectionError(f"Erro com ENABLE=broken: {exc}\nErro sem ENABLE=broken: {exc2}") from exc2
            raise ConnectionError(str(exc)) from exc

    def disconnect(self) -> None:
        if self._connection is not None:
            try:
                self._connection.close()
            except oracledb.DatabaseError:
                pass
            finally:
                self._connection = None

    def fetch_schemas(self) -> list[str]:
        return [row[0] for row in self._execute(FETCH_SCHEMAS_QUERY, {})]

    def fetch_tables(self, schema: str) -> list[str]:
        return [row[0] for row in self._execute(FETCH_TABLES_QUERY, {"schema": schema.upper()})]

    def fetch_implicit_relations(
        self, schema: str, tables: list[str]
    ) -> dict[str, dict[str, list[str]]]:
        upper_schema = schema.upper()
        upper_tables = [t.upper() for t in tables]
        placeholders = ", ".join(f":t{i}" for i in range(len(upper_tables)))
        binds: dict[str, Any] = {"schema": upper_schema}
        binds.update({f"t{i}": t for i, t in enumerate(upper_tables)})
        rows = self._execute(
            FETCH_IMPLICIT_RELATIONS_QUERY.format(
                placeholders=placeholders,
            ),
            binds,
        )
        result: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        for col_name, table_1, table_2, _ in rows:
            result[table_1][col_name].append(table_2)
            result[table_2][col_name].append(table_1)
        return {t: dict(cols) for t, cols in result.items()}

    def fetch_metadata(self, schema: str, tables: list[str]) -> list[Table]:
        if not tables:
            return []
        upper_schema = schema.upper()
        upper_tables = [t.upper() for t in tables]
        placeholders = ", ".join(f":t{i}" for i in range(len(upper_tables)))
        binds: dict[str, Any] = {"schema": upper_schema}
        binds.update({f"t{i}": t for i, t in enumerate(upper_tables)})

        col_rows = self._execute(FETCH_METADATA_QUERY.format(placeholders=placeholders), binds)
        con_rows = self._execute(FETCH_CONSTRAINTS_QUERY.format(placeholders=placeholders), binds)
        trg_rows = self._execute(FETCH_TRIGGERS_QUERY.format(placeholders=placeholders), binds)

        return self._build_tables(upper_schema, upper_tables, col_rows, con_rows, trg_rows)

    # ------------------------------------------------------------------

    def _execute(self, query: str, binds: dict[str, Any]) -> list[tuple[Any, ...]]:
        if self._connection is None:
            raise ConnectionError("Não conectado ao banco.")
        try:
            with self._connection.cursor() as cur:
                cur.execute(query, binds)
                return cur.fetchall()  # type: ignore[return-value]
        except oracledb.DatabaseError as exc:
            raise MetadataError(str(exc)) from exc

    def _build_tables(
        self,
        schema: str,
        tables: list[str],
        col_rows: list[tuple[Any, ...]],
        con_rows: list[tuple[Any, ...]],
        trg_rows: list[tuple[Any, ...]],
    ) -> list[Table]:
        cols_map: dict[str, list[Column]] = defaultdict(list)
        tbl_comment_map: dict[str, str | None] = {}
        cons_map: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        trgs_map: dict[str, list[Trigger]] = defaultdict(list)

        for row in col_rows:
            (tbl_name, order, col_name, dtype, length,
             precision, scale, nullable_str, default, col_comment, tbl_comment) = row
            tbl_comment_map.setdefault(tbl_name, tbl_comment)
            cols_map[tbl_name].append(Column(
                order=order,
                name=col_name,
                data_type=dtype,
                length=length,
                precision=precision,
                scale=scale,
                nullable=nullable_str == "Y",
                default=str(default).strip() if default is not None else None,
                comment=col_comment,
            ))

        for row in con_rows:
            tbl_name, con_name, con_type_raw, col_name, position, ref_table, ref_col, ref_pos, search_cond = row
            entry = cons_map[tbl_name].setdefault(con_name, {
                "name": con_name,
                "type": _CONSTRAINT_TYPE_MAP.get(con_type_raw, "CHECK"),
                "columns": [],
                "ref_table": ref_table,
                "ref_columns": [],
                "search_condition": str(search_cond).strip() if search_cond else None,
            })
            entry["columns"].append((position, col_name))
            if ref_col:
                entry["ref_columns"].append((ref_pos, ref_col))

        for row in trg_rows:
            tbl_name, trg_name, trg_type, trg_event, status = row
            trgs_map[tbl_name].append(Trigger(
                name=trg_name,
                trigger_type=trg_type,
                event=trg_event,
                status=status,
            ))

        return [
            Table(
                schema=schema,
                name=tbl_name,
                comment=tbl_comment_map.get(tbl_name),
                columns=tuple(cols_map.get(tbl_name, [])),
                constraints=tuple(
                    Constraint(
                        name=c["name"],
                        type=c["type"],
                        columns=tuple(col for _, col in sorted(c["columns"])),
                        ref_table=c["ref_table"],
                        ref_columns=tuple(col for _, col in sorted(c["ref_columns"])) or None,
                        search_condition=c["search_condition"],
                    )
                    for c in cons_map.get(tbl_name, {}).values()
                ),
                triggers=tuple(trgs_map.get(tbl_name, [])),
            )
            for tbl_name in tables
        ]
