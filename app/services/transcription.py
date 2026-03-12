"""
MediScribe AI — Transcription Service (Whisper Simulation).

For the MVP, this module provides a realistic simulated transcription.
When a real Whisper integration is needed, replace `transcribe_audio()`
with the OpenAI Whisper API call.
"""

import logging

logger = logging.getLogger(__name__)

# ── Sample medical consultation (Spanish) ────────────────────

SAMPLE_TRANSCRIPTION = """
Doctor: Buenos días, ¿cómo se encuentra hoy?

Paciente: Buenos días, doctor. La verdad es que no muy bien. Llevo como una semana con un dolor bastante fuerte en la parte baja de la espalda, sobre todo del lado derecho. Me cuesta mucho agacharme y por las mañanas es peor.

Doctor: Entiendo. ¿Recuerda si hizo algún esfuerzo físico antes de que empezara el dolor? ¿Levantó algo pesado, algún movimiento brusco?

Paciente: Pues sí, ahora que lo menciona, estuve ayudando a mi cuñado con una mudanza hace como diez días. Cargué varias cajas pesadas.

Doctor: Bien, eso es muy relevante. ¿Ha tenido antes problemas de espalda? ¿Alguna hernia discal diagnosticada?

Paciente: Hace como tres años me dijeron que tenía una protrusión discal en L4-L5, pero con fisioterapia se me quitó. También tengo hipertensión, tomo Losartán de 50 miligramos al día.

Doctor: De acuerdo. ¿El dolor se le irradia hacia la pierna? ¿Siente hormigueo o adormecimiento?

Paciente: Sí, a veces siento como un calambre que me baja por la pierna derecha hasta la rodilla. Y un poco de hormigueo en el pie.

Doctor: Vamos a explorarle. Recuéstese en la camilla, por favor. Voy a hacer la maniobra de Lasègue... Bien, veo que hay dolor a los 40 grados en la pierna derecha. La sensibilidad está conservada. Los reflejos rotulianos son normales. Hay contractura paravertebral a nivel lumbar derecho.

Doctor: Con base en lo que me cuenta y la exploración, mi impresión diagnóstica es una lumbalgia mecánica aguda, posiblemente con irritación radicular del nervio ciático derecho, probablemente relacionada con su antecedente de protrusión discal en L4-L5. Necesitamos confirmar con una resonancia magnética.

Doctor: Como plan de tratamiento le voy a indicar lo siguiente: primero, reposo relativo, evitar cargar peso. Le receto Diclofenaco de 75 miligramos cada 12 horas por 5 días, y Ciclobenzaprina de 10 miligramos por la noche como relajante muscular. Le solicito una resonancia magnética de columna lumbar y lo cito en dos semanas para revisar los resultados. Si el dolor empeora o pierde fuerza en la pierna, debe acudir a urgencias de inmediato.

Paciente: Muy bien, doctor. Muchas gracias.

Doctor: De nada. Cuídese mucho y no cargue cosas pesadas.
""".strip()


async def transcribe_audio(audio_path: str | None = None) -> str:
    """
    Simulate Whisper speech-to-text transcription.

    In production, this would call:
        openai.Audio.transcribe(model="whisper-1", file=audio_file)

    Args:
        audio_path: Path to audio file (ignored in MVP simulation).

    Returns:
        Raw transcription text.
    """
    logger.info(
        "🎙️  Simulando transcripción Whisper (MVP mode) — "
        "audio_path=%s",
        audio_path or "<demo>",
    )
    return SAMPLE_TRANSCRIPTION
