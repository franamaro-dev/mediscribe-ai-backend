"""
MediScribe AI — API Routes.

RESTful endpoints for medical report generation and retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.schemas.report import (
    HealthResponse,
    ReportCreate,
    ReportListResponse,
    ReportResponse,
)
from app.services import report_service

router = APIRouter(prefix="/api/v1", tags=["MediScribe AI"])


# ── Health Check ─────────────────────────────────────────────


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Verifica que el servicio esté activo.",
)
async def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )


# ── Create Report ────────────────────────────────────────────


@router.post(
    "/upload-audio",
    response_model=ReportResponse,
    status_code=201,
    summary="Generar Informe Médico",
    description=(
        "Recibe un ID de paciente y opcionalmente un texto de transcripción. "
        "Si no se proporciona transcripción, usa la demo de Whisper. "
        "Ejecuta el pipeline de IA y devuelve el informe estructurado."
    ),
)
async def upload_audio(
    data: ReportCreate,  # [SOC NOTE]: Data is automatically validated against Pydantic schema here.
    db: AsyncSession = Depends(get_db),
) -> ReportResponse:
    # [SOC NOTE]: Audit log should be triggered here in production for traceability.
    report = await report_service.create_report(data, db)
    return ReportResponse.model_validate(report)


# ── Get Single Report ────────────────────────────────────────


@router.get(
    "/reports/{report_id}",
    response_model=ReportResponse,
    summary="Obtener Informe por ID",
    description="Retorna un informe médico específico por su ID.",
)
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
) -> ReportResponse:
    report = await report_service.get_report(report_id, db)
    if report is None:
        raise HTTPException(
            status_code=404,
            detail=f"Informe con ID {report_id} no encontrado.",
        )
    return ReportResponse.model_validate(report)


# ── List Reports ─────────────────────────────────────────────


@router.get(
    "/reports",
    response_model=ReportListResponse,
    summary="Listar Informes",
    description="Retorna una lista paginada de informes médicos.",
)
async def list_reports(
    skip: int = Query(default=0, ge=0, description="Registros a omitir."),
    limit: int = Query(
        default=20, ge=1, le=100, description="Máximo de registros."
    ),
    db: AsyncSession = Depends(get_db),
) -> ReportListResponse:
    reports, total = await report_service.list_reports(db, skip=skip, limit=limit)
    return ReportListResponse(
        total=total,
        reports=[ReportResponse.model_validate(r) for r in reports],
    )
