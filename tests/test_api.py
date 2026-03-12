"""
MediScribe AI — API Tests.

Tests for all API endpoints using mocked LLM service.
"""

import pytest
from httpx import AsyncClient


# ── Health Check ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Health endpoint should return status ok."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


# ── Create Report (Demo Mode) ───────────────────────────────


@pytest.mark.asyncio
async def test_create_report_demo(client: AsyncClient):
    """Create report using simulated transcription (no API key)."""
    payload = {"patient_id": "PAC-TEST-001"}
    response = await client.post("/api/v1/upload-audio", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["patient_id"] == "PAC-TEST-001"
    assert data["status"] == "completed"
    assert data["structured_report"] is not None
    assert "motivo_consulta" in data["structured_report"]
    assert "diagnostico_presuntivo" in data["structured_report"]
    assert "plan_tratamiento" in data["structured_report"]


@pytest.mark.asyncio
async def test_create_report_custom_transcription(client: AsyncClient):
    """Create report with user-provided transcription text."""
    payload = {
        "patient_id": "PAC-TEST-002",
        "transcription_text": "Paciente acude por dolor de cabeza persistente.",
    }
    response = await client.post("/api/v1/upload-audio", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["patient_id"] == "PAC-TEST-002"
    assert data["raw_transcription"] == payload["transcription_text"]
    assert data["status"] == "completed"


# ── Get Report ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_report(client: AsyncClient):
    """Retrieve a previously created report by ID."""
    # Create first
    payload = {"patient_id": "PAC-TEST-003"}
    create_resp = await client.post("/api/v1/upload-audio", json=payload)
    report_id = create_resp.json()["id"]

    # Retrieve
    response = await client.get(f"/api/v1/reports/{report_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == report_id
    assert data["patient_id"] == "PAC-TEST-003"


@pytest.mark.asyncio
async def test_get_report_not_found(client: AsyncClient):
    """Requesting a non-existent report should return 404."""
    response = await client.get("/api/v1/reports/99999")
    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"].lower()


# ── List Reports ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_reports_empty(client: AsyncClient):
    """Listing reports when none exist should return empty list."""
    response = await client.get("/api/v1/reports")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["reports"] == []


@pytest.mark.asyncio
async def test_list_reports_with_data(client: AsyncClient):
    """Listing reports after creating some should return them."""
    # Create two reports
    for pid in ["PAC-LIST-001", "PAC-LIST-002"]:
        await client.post("/api/v1/upload-audio", json={"patient_id": pid})

    response = await client.get("/api/v1/reports")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["reports"]) == 2


@pytest.mark.asyncio
async def test_list_reports_pagination(client: AsyncClient):
    """Pagination parameters should limit results."""
    # Create 3 reports
    for i in range(3):
        await client.post(
            "/api/v1/upload-audio",
            json={"patient_id": f"PAC-PAGE-{i:03d}"},
        )

    # Request only 2
    response = await client.get("/api/v1/reports?skip=0&limit=2")
    data = response.json()
    assert data["total"] == 3
    assert len(data["reports"]) == 2


# ── Validation ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_report_missing_patient_id(client: AsyncClient):
    """Request without patient_id should return 422."""
    response = await client.post("/api/v1/upload-audio", json={})
    assert response.status_code == 422
