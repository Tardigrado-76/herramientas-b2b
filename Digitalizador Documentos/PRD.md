# PRD — LALA (OCR For All Participant Digitizer)

## Objetivo
Certificar al **100% Production Ready** la aplicación de escritorio **LALA** (PySide6 + EasyOCR + RapidFuzz + OpenCV) bajo arquitectura soberana nativa en Windows 11 (**Cero-Docker Absoluto**) y cumplimiento estricto de privacidad GDPR / TOMs (filtrado de columnas de firmas manuscritas).

## Hitos de Ingeniería y Calidad (Ralph Loop)
- [x] **Inicialización Perezosa (Lazy Loading) de EasyOCR:** Refactorización de `OCRService.__init__` hacia `@property def reader` (`self._reader = None`) evitando accesos a disco en `C:\Users\josel\.EasyOCR\model` durante la instanciación o tests geométricos.
- [x] **Mocking Global y Expansión TDD (`tests/test_services.py`):** Implementación de fixture `@pytest.fixture(autouse=True)` para `easyocr.Reader` y ampliación a 14 tests unitarios y de integración (geometría OCR, filtrado GDPR de columnas de firma, normalización Unicode, RapidFuzz matching, persistencia Excel y Workers Qt).
- [x] **Auditoría Code Doctor (Ruff + Mypy 0 Errores):**
  - [x] Eliminación de importaciones no utilizadas en `config.py`, `gui/main_window.py`, `gui/worker.py`, `sample_data/generate_samples.py` y `tests/test_services.py`.
  - [x] Corrección de iteración sobre documento PyMuPDF (`range(len(doc))`) y tupla `(pix.width, pix.height)` en `Image.frombytes`.
  - [x] Anotación `ClassVar` en atributos de clase mutables de `OCRService` y tipado explícito `Image.Image`.
  - [x] Conversión de `IOError` a `OSError` y `datetime.now(tz=timezone.utc)` en `services/data_service.py` y `gui/main_window.py`.
  - [x] Seguridad de tipos en `QSettings.value` (`str(...)`) y guardia contra `None` en `QTableWidget.item()` y `horizontalHeaderItem()`.
- [x] **Lanzador Nativo Desatendido (`INICIAR_LALA_HUB.bat`):** Consola interactiva UTF-8 (`chcp 65001 >nul`) con arranque de GUI PySide6, ejecución de suite Pytest TDD, auditoría Code Doctor y generador de muestras sintéticas.
- [x] **Externalización de Memoria Operativa (`PRD.md` y `progress.txt`):** Registro completo y trazable.
