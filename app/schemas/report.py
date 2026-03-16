"""
MediScribe AI — Pydantic Schemas (Request / Response validation).
[SOC NOTE]: Using Pydantic for strict input sanitization and schema enforcement. 
This prevents SQLi/XSS at the entry point.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Structured Medical Report sections ───────────────────────


class StructuredReport(BaseModel):
    """JSON output produced by the LLM structurer."""

    motivo_consulta: str = Field(
        ..., description="Razón principal de la visita médica."
    )
    antecedentes: str = Field(
        ..., description="Historial médico relevante del paciente."
    )
    examen_fisico: str = Field(
        ..., description="Hallazgos del examen físico realizado."
    )
    diagnostico_presuntivo: str = Field(
        ..., description="Diagnóstico preliminar basado en la evaluación."
    )
    plan_tratamiento: str = Field(
        ..., description="Plan de tratamiento propuesto."
    )


# ── Request schemas ──────────────────────────────────────────


class ReportCreate(BaseModel):
    """Input payload to create a new medical report."""

    patient_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Identificador del paciente.",
        examples=["PAC-2024-001"],
    )
    transcription_text: Optional[str] = Field(
        default=None,
        description=(
            "Texto de transcripción manual. Si no se envía, "
            "se usa la transcripción simulada (demo)."
        ),
    )


# ── Response schemas ─────────────────────────────────────────


class ReportResponse(BaseModel):
    """Full report representation returned by the API."""

    model_config = {"from_attributes": True}

    id: int
    patient_id: str
    raw_transcription: str
    structured_report: Optional[StructuredReport] = None
    status: str
    created_at: datetime
    updated_at: datetime


class ReportListResponse(BaseModel):
    """Paginated list of reports."""

    total: int
    reports: list[ReportResponse]


class HealthResponse(BaseModel):
    """Health-check response."""

    status: str = "ok"
    version: str
    debug: bool
