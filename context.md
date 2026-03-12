# MediScribe AI - Project Context

## 🎯 Visión General
MVP de un backend para la automatización de informes médicos. Transforma audio (simulado) en informes estructurados JSON usando IA.

## 🛠️ Stack Tecnológico
- **Framework:** FastAPI (Python 3.11+)
- **IA/NLP:** LangChain + OpenAI (GPT-4o-mini). Incluye demo mode/mock fallback.
- **Base de Datos:** SQLite con SQLAlchemy (Async).
- **Validación:** Pydantic v2.
- **Testing:** Pytest + Pytest-Asyncio.

## 🏗️ Arquitectura (Clean Architecture)
- `api/`: Rutas REST versionadas.
- `core/`: Configuración y engine de base de datos.
- `models/`: Definición de tablas SQLAlchemy.
- `schemas/`: Contratos de datos Pydantic.
- `services/`: Lógica de negocio y pipeline de IA.

## 📌 Decisiones Clave (ADR)
1. **Mock Fallback:** El servicio de LLM devuelve datos realistas si no hay API Key, permitiendo desarrollo offline/demo.
2. **Async DB:** Uso de `aiosqlite` para evitar bloqueos en el event loop de FastAPI.
3. **Lifespan Handler:** Inicialización automática de tablas al arrancar la app.

## 🚀 Repositorio
[https://github.com/franamaro-dev/mediscribe-ai-backend](https://github.com/franamaro-dev/mediscribe-ai-backend)

## 📝 Próximos Pasos (Roadmap)
- Integración real con Whisper API.
- Soporte multi-idioma.
- Validación con SNOMED-CT / CIE-11.
- Autenticación JWT.
