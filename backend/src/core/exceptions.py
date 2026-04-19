class RelationalsDocError(Exception):
    """Base exception para todos os erros do domínio."""


class ConnectionError(RelationalsDocError):
    """Falha ao conectar ou autenticar no banco de dados."""


class MetadataError(RelationalsDocError):
    """Falha ao buscar metadados das tabelas."""


class RenderError(RelationalsDocError):
    """Falha ao renderizar o markdown de uma tabela."""


class TunnelError(RelationalsDocError):
    """Falha ao abrir ou fechar o túnel SSH."""
