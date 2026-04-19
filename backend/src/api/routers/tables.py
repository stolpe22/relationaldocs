import asyncio
import io
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from adapters import get_reader
from api.dependencies import verify_api_key
from api.schemas.tables import (
    AnalysisRequest,
    AnalysisResponse,
    GenerateRequest,
    GenerateResponse,
    ImplicitRelation,
    JobStatusResponse,
    SchemasResponse,
    TableSummary,
    TablesResponse,
)
from api.state import app_state
from core.exceptions import ConnectionError, MetadataError
from services.markdown_service import MarkdownService

router = APIRouter(prefix="/api/v1", tags=["tables"], dependencies=[Depends(verify_api_key)])

_JOB_TTL_SECONDS = 600


def _get_reader_connected(  # type: ignore[no-untyped-def]
    db_type: str, host: str, port: int, service: str, user: str, password: str,
    connection_type: str = "service_name",
):
    reader_cls = get_reader(db_type)
    tunnel = app_state.tunnel
    active = tunnel is not None and tunnel.is_active
    actual_host = "127.0.0.1" if active else host
    actual_port = tunnel.local_bind_port if (active and tunnel) else port
    reader = reader_cls(
        host=actual_host, port=actual_port, service_name=service, user=user, password=password,
        connection_type=connection_type,
    )
    try:
        reader.connect()
    except ConnectionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return reader


@router.get("/schemas", summary="Lista schemas disponíveis", response_model=SchemasResponse)
async def list_schemas(
    db_type: str = Query(default="oracle"),
    host: str = Query(...),
    port: int = Query(...),
    service: str = Query(...),
    user: str = Query(...),
    password: str = Query(...),
) -> SchemasResponse:
    reader = _get_reader_connected(db_type, host, port, service, user, password)
    try:
        schemas = reader.fetch_schemas()
        return SchemasResponse(schemas=schemas)
    except MetadataError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        reader.disconnect()


@router.get("/tables", summary="Lista tabelas do schema com paginação", response_model=TablesResponse)  # noqa: E501
async def list_tables(
    schema: str = Query(...),
    db_type: str = Query(default="oracle"),
    host: str = Query(...),
    port: int = Query(...),
    service: str = Query(...),
    user: str = Query(...),
    password: str = Query(...),
    limit: int = Query(default=5000, ge=1, le=10000),
    offset: int = Query(default=0, ge=0),
) -> TablesResponse:
    reader = _get_reader_connected(db_type, host, port, service, user, password)
    try:
        all_tables = reader.fetch_tables(schema)
        page = all_tables[offset: offset + limit]
        return TablesResponse(tables=page, total=len(all_tables), limit=limit, offset=offset)
    except MetadataError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        reader.disconnect()


@router.post("/analysis", summary="Dashboard analítico das tabelas", response_model=AnalysisResponse)  # noqa: E501
async def analyse(body: AnalysisRequest) -> AnalysisResponse:
    conn = app_state.connection
    if conn is None:
        raise HTTPException(status_code=400, detail="Nenhuma conexão ativa. Conecte-se primeiro.")
    reader = _get_reader_connected(
        conn.db_type, conn.host, conn.port, conn.service_name, conn.user, conn.password,
        connection_type=conn.connection_type,
    )
    try:
        tables = reader.fetch_metadata(body.schema_name, body.tables)
        implicit_raw = reader.fetch_implicit_relations(body.schema_name, body.tables)
        selected_names = set(body.tables)
        table_summaries = []
        for t in tables:
            fk_targets = [c.ref_table for c in t.constraints if c.type == "FK" and c.ref_table]
            table_summaries.append(TableSummary(
                name=t.name,
                columns=len(t.columns),
                pks=sum(1 for c in t.constraints if c.type == "PK"),
                fks=sum(1 for c in t.constraints if c.type == "FK"),
                uks=sum(1 for c in t.constraints if c.type == "UK"),
                checks=sum(1 for c in t.constraints if c.type == "CHECK"),
                triggers=len(t.triggers),
                referenced_tables=sorted(set(fk_targets)),
            ))
        all_refs = {r for s in table_summaries for r in s.referenced_tables}
        external_refs = sorted(all_refs - selected_names)

        # Deduplicar pares implícitos (A-B e B-A viram um único registro)
        seen: set[tuple[str, str, str]] = set()
        implicit_list: list[ImplicitRelation] = []
        for tbl_name, col_map in implicit_raw.items():
            for col_name, related in col_map.items():
                for other in related:
                    pair = (col_name, *sorted([tbl_name, other]))
                    if pair not in seen:
                        seen.add(pair)
                        implicit_list.append(ImplicitRelation(
                            column=col_name, table_1=pair[1], table_2=pair[2]
                        ))
        implicit_list.sort(key=lambda r: (r.column, r.table_1, r.table_2))

        return AnalysisResponse(
            total_tables=len(tables),
            total_columns=sum(s.columns for s in table_summaries),
            total_pks=sum(s.pks for s in table_summaries),
            total_fks=sum(s.fks for s in table_summaries),
            total_uks=sum(s.uks for s in table_summaries),
            total_checks=sum(s.checks for s in table_summaries),
            total_triggers=sum(s.triggers for s in table_summaries),
            total_constraints=sum(s.pks + s.fks + s.uks + s.checks for s in table_summaries),
            external_references=external_refs,
            implicit_relations=implicit_list,
            tables=table_summaries,
        )
    except MetadataError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        reader.disconnect()


@router.post(
    "/generate",
    summary="Gera documentação (async)",
    response_model=GenerateResponse,
    status_code=202,
)
async def generate(body: GenerateRequest, background_tasks: BackgroundTasks) -> GenerateResponse:
    job_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(seconds=_JOB_TTL_SECONDS)
    app_state.jobs[job_id] = {
        "status": "pending", "result": None, "error": None, "expires_at": expires_at
    }
    background_tasks.add_task(_run_generate, job_id, body)
    return GenerateResponse(job_id=job_id)


@router.get("/jobs/{job_id}", summary="Status do job de geração", response_model=JobStatusResponse)
async def job_status(job_id: str) -> JobStatusResponse:
    job = app_state.jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job não encontrado ou expirado.")
    return JobStatusResponse(job_id=job_id, status=job["status"], error=job.get("error"))


@router.get("/jobs/{job_id}/download", summary="Download do ZIP gerado")
async def job_download(job_id: str) -> StreamingResponse:
    job = app_state.jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job não encontrado ou expirado.")
    if job["status"] != "done":
        raise HTTPException(status_code=400, detail=f"Job ainda em '{job['status']}'.")
    zip_bytes: bytes = job["result"]
    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=docs_{job_id[:8]}.zip"},
    )


async def _run_generate(job_id: str, body: GenerateRequest) -> None:
    job = app_state.jobs[job_id]
    job["status"] = "running"
    try:
        await asyncio.sleep(0)
        conn = app_state.connection
        if conn is None:
            raise RuntimeError("Nenhuma conexão ativa.")
        reader = _get_reader_connected(
            conn.db_type, conn.host, conn.port, conn.service_name, conn.user, conn.password,
            connection_type=conn.connection_type,
        )
        try:
            tables = reader.fetch_metadata(body.schema_name, body.tables)
            implicit = reader.fetch_implicit_relations(body.schema_name, body.tables)
        finally:
            reader.disconnect()
        service = MarkdownService()
        zip_bytes = service.generate_zip(schema=body.schema_name, tables=tables, implicit=implicit)
        job["status"] = "done"
        job["result"] = zip_bytes
    except Exception as exc:
        job["status"] = "error"
        job["error"] = str(exc)
