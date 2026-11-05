"""Background thread workers for asynchronous execution in PySide6.

Prevents GUI freezing during OpenAI Vision AI network calls, Excel file I/O,
and computationally intensive fuzzy matching algorithms.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QThread, Signal

from services.data_service import (
    DataService,
    FuzzyMatchResult,
)
from services.ocr_service import OCRService


class OCRWorker(QThread):
    """Worker thread to execute OCR / Vision AI analysis in the background."""

    sig_log = Signal(str, str)  # (message, level: "INFO" | "SUCCESS" | "WARNING" | "ERROR")
    sig_progress = Signal(int)  # 0 - 100
    sig_finished = Signal(list)  # list[dict[str, Any]]
    sig_error = Signal(str)

    def __init__(
        self,
        file_path: str,
        parent: Any = None,
    ) -> None:
        super().__init__(parent)
        self.file_path = file_path

    def run(self) -> None:
        """Execute Vision AI extraction."""
        try:
            self.sig_progress.emit(15)
            self.sig_log.emit(
                f"Iniciando análisis OCR local sobre archivo: '{self.file_path}'", "INFO"
            )

            service = OCRService()
            self.sig_progress.emit(35)
            self.sig_log.emit("Procesando imagen con modelo EasyOCR (Local)...", "INFO")

            records = service.extract_form_data(file_path=self.file_path)

            self.sig_progress.emit(90)
            self.sig_log.emit(
                f"OCR completado exitosamente: Se detectaron {len(records)} registro(s) estructurado(s).",
                "SUCCESS",
            )
            self.sig_progress.emit(100)
            self.sig_finished.emit(records)

        except Exception as e:  # noqa: BLE001
            self.sig_progress.emit(0)
            err_msg = str(e)
            self.sig_log.emit(f"Fallo en el análisis OCR: {err_msg}", "ERROR")
            self.sig_error.emit(err_msg)


class ValidationWorker(QThread):
    """Worker thread to validate Excel headers and enrich with master list via rapidfuzz."""

    sig_log = Signal(str, str)
    sig_progress = Signal(int)
    sig_finished = Signal(object, object)  # (HeaderValidationResult, FuzzyMatchResult | None)
    sig_error = Signal(str)

    def __init__(
        self,
        records: list[dict[str, Any]],
        target_path: str,
        master_path: str | None = None,
        threshold: float = 72.0,
        parent: Any = None,
    ) -> None:
        super().__init__(parent)
        self.records = records
        self.target_path = target_path
        self.master_path = master_path
        self.threshold = threshold

    def run(self) -> None:
        """Execute validation and fuzzy matching."""
        try:
            self.sig_progress.emit(10)
            self.sig_log.emit("Iniciando validación de cabeceras y esquema...", "INFO")

            # Extract list of columns from current records
            all_cols: set[str] = set()
            for r in self.records:
                all_cols.update(r.keys())
            col_list = sorted(all_cols)

            header_res = DataService.validate_headers(
                target_path=self.target_path,
                extracted_columns=col_list,
            )

            for msg in header_res.messages:
                lvl = "INFO" if header_res.is_compatible else "WARNING"
                self.sig_log.emit(msg, lvl)

            self.sig_progress.emit(50)

            fuzzy_res: FuzzyMatchResult | None = None
            if self.master_path and self.master_path.strip():
                self.sig_log.emit(
                    f"Iniciando cruce de datos con listado maestro: '{self.master_path}' (Umbral: {self.threshold}%)...",
                    "INFO",
                )
                fuzzy_res = DataService.enrich_with_master(
                    records=self.records,
                    master_path=self.master_path,
                    threshold=self.threshold,
                )
                for log_line in fuzzy_res.logs:
                    lvl = "SUCCESS" if "Coincidencia" in log_line or "finalizado" in log_line else "WARNING"
                    self.sig_log.emit(log_line, lvl)
            else:
                self.sig_log.emit(
                    "No se indicó listado maestro de participantes. Se omite el cruce difuso.",
                    "INFO",
                )

            self.sig_progress.emit(100)
            self.sig_finished.emit(header_res, fuzzy_res)

        except Exception as e:  # noqa: BLE001
            self.sig_progress.emit(0)
            err_msg = str(e)
            self.sig_log.emit(f"Error durante la validación o enriquecimiento: {err_msg}", "ERROR")
            self.sig_error.emit(err_msg)


class ConsolidationWorker(QThread):
    """Worker thread to append records into target Excel workbook."""

    sig_log = Signal(str, str)
    sig_progress = Signal(int)
    sig_finished = Signal(object)  # PersistResult
    sig_error = Signal(str)

    def __init__(
        self,
        records: list[dict[str, Any]],
        target_path: str,
        create_if_not_exists: bool = True,
        parent: Any = None,
    ) -> None:
        super().__init__(parent)
        self.records = records
        self.target_path = target_path
        self.create_if_not_exists = create_if_not_exists

    def run(self) -> None:
        """Execute persistence into Excel."""
        try:
            self.sig_progress.emit(20)
            self.sig_log.emit(f"Guardando datos en archivo Excel: '{self.target_path}'...", "INFO")

            persist_res = DataService.persist_to_excel(
                records=self.records,
                target_path=self.target_path,
                create_if_not_exists=self.create_if_not_exists,
            )

            self.sig_progress.emit(90)
            self.sig_log.emit(persist_res.message, "SUCCESS")
            self.sig_progress.emit(100)
            self.sig_finished.emit(persist_res)

        except Exception as e:  # noqa: BLE001
            self.sig_progress.emit(0)
            err_msg = str(e)
            self.sig_log.emit(f"Error al consolidar en Excel: {err_msg}", "ERROR")
            self.sig_error.emit(err_msg)
