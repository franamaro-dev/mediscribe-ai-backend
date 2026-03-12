"""
MediScribe AI — LLM Structurer Service.

Uses LangChain + OpenAI to transform raw medical transcriptions
into structured clinical reports.
"""

import json
import logging

from app.core.config import get_settings
from app.schemas.report import StructuredReport

logger = logging.getLogger(__name__)

# ── Medical prompt template ──────────────────────────────────

SYSTEM_PROMPT = """Eres un asistente médico especializado en documentación clínica.
Tu tarea es analizar la transcripción de una consulta médica y extraer
la información relevante para generar un informe clínico estructurado.

Debes devolver ÚNICAMENTE un JSON válido con las siguientes claves exactas:

{{
  "motivo_consulta": "Razón principal por la que el paciente acude a consulta",
  "antecedentes": "Historial médico relevante mencionado durante la consulta",
  "examen_fisico": "Hallazgos del examen físico realizado por el médico",
  "diagnostico_presuntivo": "Diagnóstico o impresión clínica del médico",
  "plan_tratamiento": "Tratamiento indicado, medicamentos, estudios y seguimiento"
}}

REGLAS:
- Usa lenguaje médico profesional pero claro.
- Incluye todos los detalles específicos (dosis, frecuencias, medidas).
- No inventes información que no esté en la transcripción.
- Responde SOLO con el JSON, sin texto adicional.
"""

HUMAN_PROMPT = """Transcripción de consulta médica:

{transcription}

Genera el informe clínico estructurado en formato JSON."""

# ── Mock fallback (no API key) ───────────────────────────────

MOCK_REPORT = StructuredReport(
    motivo_consulta=(
        "Dolor lumbar bajo de predominio derecho de una semana de evolución, "
        "con irradiación a miembro inferior derecho. Exacerbación matutina "
        "y limitación funcional para la flexión del tronco."
    ),
    antecedentes=(
        "Protrusión discal L4-L5 diagnosticada hace 3 años, resuelta con "
        "fisioterapia. Hipertensión arterial en tratamiento con Losartán "
        "50 mg/día. Esfuerzo físico reciente (carga de objetos pesados "
        "durante mudanza hace 10 días)."
    ),
    examen_fisico=(
        "Maniobra de Lasègue positiva a 40° en miembro inferior derecho. "
        "Sensibilidad conservada. Reflejos osteotendinosos rotulianos "
        "normales y simétricos. Contractura paravertebral lumbar derecha "
        "a la palpación."
    ),
    diagnostico_presuntivo=(
        "Lumbalgia mecánica aguda con probable irritación radicular del "
        "nervio ciático derecho, asociada a antecedente de protrusión "
        "discal L4-L5."
    ),
    plan_tratamiento=(
        "1) Reposo relativo, evitar carga de peso. "
        "2) Diclofenaco 75 mg cada 12 horas por 5 días. "
        "3) Ciclobenzaprina 10 mg por la noche (relajante muscular). "
        "4) Solicitud de resonancia magnética de columna lumbar. "
        "5) Control en 2 semanas para revisión de resultados. "
        "6) Signos de alarma: acudir a urgencias si el dolor empeora "
        "o presenta pérdida de fuerza en la pierna."
    ),
)


async def structure_transcription(transcription: str) -> StructuredReport:
    """
    Process raw transcription through LLM to extract structured report.

    Falls back to mock data if OPENAI_API_KEY is not configured.

    Args:
        transcription: Raw text from speech-to-text.

    Returns:
        Validated StructuredReport with medical sections.
    """
    settings = get_settings()

    if not settings.OPENAI_API_KEY:
        logger.warning(
            "⚠️  OPENAI_API_KEY no configurada — usando respuesta mock."
        )
        return MOCK_REPORT

    # ── Real LLM call via LangChain ──────────────────────────
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=settings.OPENAI_API_KEY,
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=HUMAN_PROMPT.format(transcription=transcription)
            ),
        ]

        logger.info("🤖 Enviando transcripción al LLM (gpt-4o-mini)...")
        response = await llm.ainvoke(messages)

        # Parse JSON from LLM response
        raw_json = response.content.strip()
        # Remove markdown code fences if present
        if raw_json.startswith("```"):
            raw_json = raw_json.split("\n", 1)[1]
            raw_json = raw_json.rsplit("```", 1)[0]

        parsed = json.loads(raw_json)
        report = StructuredReport(**parsed)

        logger.info("✅ Informe estructurado generado exitosamente.")
        return report

    except Exception as exc:
        logger.error("❌ Error al procesar con LLM: %s", exc)
        logger.info("↩️  Retornando respuesta mock como fallback.")
        return MOCK_REPORT
