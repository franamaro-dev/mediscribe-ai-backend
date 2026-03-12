"""
MediScribe AI — Report Service (Business Logic).

Orchestrates the full pipeline: transcribe → structure → persist.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import MedicalReport, ReportStatus
from app.schemas.report import ReportCreate
from app.services.llm_structurer import structure_transcription
from app.services.transcription import transcribe_audio

logger = logging.getLogger(__name__)


async def create_report(
    data: ReportCreate,
    db: AsyncSession,
) -> MedicalReport:
    """
    Full pipeline: transcription → LLM structuring → database persistence.

    Args:
        data: Input payload (patient_id + optional transcription).
        db: Async database session.

    Returns:
        Persisted MedicalReport ORM instance.
    """
    # Step 1: Transcription
    if data.transcription_text:
        raw_text = data.transcription_text
        logger.info("📝 Usando transcripción proporcionada por el usuario.")
    else:
        raw_text = await transcribe_audio()
        logger.info("🎙️  Usando transcripción simulada (Whisper demo).")

    # Create report in PROCESSING state
    report = MedicalReport(
        patient_id=data.patient_id,
        raw_transcription=raw_text,
        status=ReportStatus.PROCESSING,
    )
    db.add(report)
    await db.flush()
    logger.info("📋 Report ID=%s creado (status=processing).", report.id)

    # Step 2: LLM Structuring
    try:
        structured = await structure_transcription(raw_text)
        report.structured_report = structured.model_dump()
        report.status = ReportStatus.COMPLETED
        report.updated_at = datetime.now(timezone.utc)
        logger.info("✅ Report ID=%s completado.", report.id)
    except Exception as exc:
        report.status = ReportStatus.ERROR
        report.updated_at = datetime.now(timezone.utc)
        logger.error("❌ Error en pipeline para report ID=%s: %s", report.id, exc)

    await db.flush()
    return report


async def get_report(report_id: int, db: AsyncSession) -> MedicalReport | None:
    """Retrieve a single report by ID."""
    result = await db.execute(
        select(MedicalReport).where(MedicalReport.id == report_id)
    )
    return result.scalar_one_or_none()


async def list_reports(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[MedicalReport], int]:
    """
    List reports with pagination.

    Returns:
        Tuple of (reports_list, total_count).
    """
    # Count
    count_result = await db.execute(
        select(func.count()).select_from(MedicalReport)
    )
    total = count_result.scalar_one()

    # Query
    result = await db.execute(
        select(MedicalReport)
        .order_by(MedicalReport.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    reports = list(result.scalars().all())

    return reports, total
