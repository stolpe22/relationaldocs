from pydantic import BaseModel, ConfigDict, Field


class SchemasResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    schemas: list[str]


class TablesResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    tables: list[str]
    total: int
    limit: int
    offset: int


class AnalysisRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    schema_name: str
    tables: list[str] = Field(min_length=1)


class TableSummary(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    columns: int
    pks: int
    fks: int
    uks: int
    checks: int
    triggers: int
    referenced_tables: list[str]


class ImplicitRelation(BaseModel):
    model_config = ConfigDict(strict=True)

    column: str
    table_1: str
    table_2: str


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    total_tables: int
    total_columns: int
    total_pks: int
    total_fks: int
    total_uks: int
    total_checks: int
    total_triggers: int
    total_constraints: int
    external_references: list[str]
    implicit_relations: list[ImplicitRelation]
    tables: list[TableSummary]


class GenerateRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    schema_name: str
    tables: list[str] = Field(min_length=1)


class GenerateResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    job_id: str


class JobStatusResponse(BaseModel):
    model_config = ConfigDict(strict=True)

    job_id: str
    status: str  # pending | running | done | error
    error: str | None = None
