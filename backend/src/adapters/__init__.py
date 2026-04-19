from adapters.oracle.reader import OracleReader
from core.interfaces.database_reader import DatabaseReader

SUPPORTED_DATABASES: dict[str, type[DatabaseReader]] = {
    "oracle": OracleReader,
    # "postgres":  PostgresReader,   # futuro
    # "sqlserver": SqlServerReader,  # futuro
    # "mysql":     MySQLReader,      # futuro
}


def get_reader(db_type: str) -> type[DatabaseReader]:
    reader_cls = SUPPORTED_DATABASES.get(db_type.lower())
    if reader_cls is None:
        supported = ", ".join(SUPPORTED_DATABASES)
        raise ValueError(f"Banco '{db_type}' não suportado. Suportados: {supported}")
    return reader_cls
