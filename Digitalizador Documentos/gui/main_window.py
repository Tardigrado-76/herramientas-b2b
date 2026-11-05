"""Main Window implementation for LALA Desktop Application.

Provides an executive-grade PySide6 GUI with:
- Multi-file selection with validation
- Interactive editable QTableWidget preview
- Real-time formatted log console
- Async action triggers (Analyze, Validate & Enrich, Consolidate)
- Live API Key status and configuration dialog
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import (
    QDragEnterEvent,
    QDropEvent,
    QFont,
    QKeySequence,
    QShortcut,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config import AppConfig
from gui.styles import CORPORATE_DARK_STYLESHEET
from gui.worker import ConsolidationWorker, OCRWorker, ValidationWorker
from services.data_service import (
    FuzzyMatchResult,
    HeaderValidationResult,
    PersistResult,
)


class DropLineEdit(QLineEdit):
    """A QLineEdit that accepts drag and drop of files."""
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            self.setText(urls[0].toLocalFile())
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

class MainWindow(QMainWindow):
    """Main application window for LALA."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{AppConfig.APP_NAME} v{AppConfig.APP_VERSION}")
        self.resize(1200, 800)
        self.setStyleSheet(CORPORATE_DARK_STYLESHEET)

        # Worker references
        self._active_worker: Any = None

        # Internal state
        self._current_records: list[dict[str, Any]] = []
        self.settings = QSettings("LALA", "LALA-App")

        self._setup_ui()
        self._load_settings()

        self.log(
            f"Bienvenido a {AppConfig.APP_NAME}. Sistema inicializado y listo.",
            "INFO",
        )

    def _setup_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(18, 14, 18, 14)
        main_layout.setSpacing(12)

        # 1. Header with title & API key status
        header_layout = QHBoxLayout()
        header_title_layout = QVBoxLayout()
        title_lbl = QLabel(AppConfig.APP_NAME)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_lbl.setFont(title_font)
        title_lbl.setStyleSheet("color: #60a5fa;")

        subtitle_lbl = QLabel("Extracción inteligente de formularios manuscritos y consolidación automatizada en Excel")
        subtitle_lbl.setStyleSheet("color: #9ca3af; font-size: 11px;")
        header_title_layout.addWidget(title_lbl)
        header_title_layout.addWidget(subtitle_lbl)

        header_layout.addLayout(header_title_layout)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # 2. File Selectors Panel (QGroupBox)
        files_group = QGroupBox("1. Origen de Datos y Destinos de Consolidación")
        files_layout = QVBoxLayout(files_group)
        files_layout.setSpacing(8)

        # Selector 1: Formulario manuscrito (Image/PDF)
        row1 = QHBoxLayout()
        lbl1 = QLabel("Formulario Manuscrito (Img/PDF):")
        lbl1.setFixedWidth(200)
        self.edit_form_path = DropLineEdit()
        self.edit_form_path.setPlaceholderText("Arrastre aquí la imagen o documento PDF (.png, .jpg, .pdf)...")
        btn_browse_form = QPushButton("Examinar...")
        btn_browse_form.setFixedWidth(110)
        btn_browse_form.clicked.connect(self._browse_form_file)
        row1.addWidget(lbl1)
        row1.addWidget(self.edit_form_path)
        row1.addWidget(btn_browse_form)
        files_layout.addLayout(row1)

        # Selector 2: Excel de Destino + Checkbox Crear nuevo
        row2 = QHBoxLayout()
        lbl2 = QLabel("Excel de Destino:")
        lbl2.setFixedWidth(200)
        self.edit_target_excel = DropLineEdit()
        self.edit_target_excel.setPlaceholderText("Arrastre o indique la ruta del Excel (.xlsx)...")
        btn_browse_target = QPushButton("Examinar...")
        btn_browse_target.setFixedWidth(110)
        btn_browse_target.clicked.connect(self._browse_target_excel)
        self.cb_create_if_not_exists = QCheckBox("Crear nuevo si no existe")
        self.cb_create_if_not_exists.setChecked(True)
        row2.addWidget(lbl2)
        row2.addWidget(self.edit_target_excel)
        row2.addWidget(btn_browse_target)
        row2.addWidget(self.cb_create_if_not_exists)
        files_layout.addLayout(row2)

        # Selector 3: Listado Maestro (Opcional)
        row3 = QHBoxLayout()
        lbl3 = QLabel("Listado Maestro (Opcional):")
        lbl3.setFixedWidth(200)
        self.edit_master_excel = DropLineEdit()
        self.edit_master_excel.setPlaceholderText("Ruta del listado maestro de referencia (Opcional)...")
        btn_browse_master = QPushButton("Examinar...")
        btn_browse_master.setFixedWidth(110)
        btn_browse_master.clicked.connect(self._browse_master_excel)
        btn_clear_master = QPushButton("Limpiar")
        btn_clear_master.setFixedWidth(80)
        btn_clear_master.clicked.connect(lambda: self.edit_master_excel.clear())
        row3.addWidget(lbl3)
        row3.addWidget(self.edit_master_excel)
        row3.addWidget(btn_browse_master)
        row3.addWidget(btn_clear_master)
        files_layout.addLayout(row3)

        main_layout.addWidget(files_group)

        # 3. Middle Section: Splitter with Table Preview on top/left and Log Console on bottom/right
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(6)

        # --- Table Preview Container ---
        table_container = QGroupBox("2. Previsualización y Edición de Datos Extraídos")
        table_layout = QVBoxLayout(table_container)
        table_layout.setSpacing(6)

        # Table controls bar (Add Row, Delete Row, Clear)
        table_actions = QHBoxLayout()
        self.lbl_table_count = QLabel("0 filas detectadas | Las celdas son editables directamente")
        self.lbl_table_count.setStyleSheet("color: #93c5fd; font-size: 11px;")
        table_actions.addWidget(self.lbl_table_count)
        table_actions.addStretch()

        btn_add_row = QPushButton("+ Agregar Fila")
        btn_add_row.clicked.connect(self._add_table_row)
        btn_del_row = QPushButton("- Eliminar Fila")
        btn_del_row.clicked.connect(self._delete_selected_row)
        btn_clear_table = QPushButton("Limpiar Tabla")
        btn_clear_table.clicked.connect(self._clear_table)

        table_actions.addWidget(btn_add_row)
        table_actions.addWidget(btn_del_row)
        table_actions.addWidget(btn_clear_table)
        table_layout.addLayout(table_actions)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        table_layout.addWidget(self.table)
        splitter.addWidget(table_container)

        # --- Console Log Container ---
        log_container = QGroupBox("3. Consola de Registro y Auditoría en Vivo")
        log_layout = QVBoxLayout(log_container)
        log_layout.setSpacing(6)

        log_actions = QHBoxLayout()
        log_lbl_hint = QLabel("Eventos de extracción, comparativa de columnas y similitud difusa:")
        log_lbl_hint.setStyleSheet("color: #9ca3af; font-size: 11px;")
        log_actions.addWidget(log_lbl_hint)
        log_actions.addStretch()

        btn_clear_log = QPushButton("Limpiar Consola")
        btn_clear_log.clicked.connect(self._clear_log)
        log_actions.addWidget(btn_clear_log)
        log_layout.addLayout(log_actions)

        self.console = QTextEdit()
        self.console.setObjectName("console_log")
        self.console.setReadOnly(True)
        log_layout.addWidget(self.console)
        splitter.addWidget(log_container)

        splitter.setSizes([420, 220])
        main_layout.addWidget(splitter, stretch=1)

        # 4. Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)

        # 5. Action Buttons Bar
        actions_frame = QFrame()
        actions_frame.setObjectName("card")
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(8, 8, 8, 8)
        actions_layout.setSpacing(12)

        self.btn_analyze = QPushButton("1. Analizar Formulario (OCR for all)")
        self.btn_analyze.setObjectName("primary_button")
        self.btn_analyze.clicked.connect(self.on_analyze_clicked)

        self.btn_validate = QPushButton("2. Validar & Enriquecer (Fuzzy Match)")
        self.btn_validate.setObjectName("secondary_button")
        self.btn_validate.clicked.connect(self.on_validate_clicked)

        self.btn_consolidate = QPushButton("3. Consolidar en Excel")
        self.btn_consolidate.setObjectName("success_button")
        self.btn_consolidate.clicked.connect(self.on_consolidate_clicked)

        actions_layout.addWidget(self.btn_analyze)
        actions_layout.addWidget(self.btn_validate)
        actions_layout.addWidget(self.btn_consolidate)
        main_layout.addWidget(actions_frame)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo")

        # Shortcuts
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self._add_table_row)
        QShortcut(QKeySequence("Del"), self.table).activated.connect(self._delete_selected_row)

    def closeEvent(self, event: Any) -> None:
        """Save settings before closing."""
        self._save_settings()
        super().closeEvent(event)

    def _load_settings(self) -> None:
        """Load last used file paths."""
        self.edit_target_excel.setText(str(self.settings.value("last_target_excel", "") or ""))
        self.edit_master_excel.setText(str(self.settings.value("last_master_excel", "") or ""))

    def _save_settings(self) -> None:
        """Save current file paths to QSettings."""
        self.settings.setValue("last_target_excel", self.edit_target_excel.text().strip())
        self.settings.setValue("last_master_excel", self.edit_master_excel.text().strip())

    # -------------------------------------------------------------------------
    # File Browsers
    # -------------------------------------------------------------------------
    def _browse_form_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Formulario Manuscrito",
            "",
            "Archivos Compatibles (*.png *.jpg *.jpeg *.webp *.bmp *.pdf);;Imágenes (*.png *.jpg *.jpeg *.webp *.bmp);;Documentos PDF (*.pdf);;Todos los archivos (*.*)",
        )
        if file_path:
            self.edit_form_path.setText(file_path)
            self.log(f"Formulario manuscrito seleccionado: '{file_path}'", "INFO")

    def _browse_target_excel(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Seleccionar o Especificar Excel de Destino",
            "",
            "Libro de Excel (*.xlsx);;Todos los archivos (*.*)",
        )
        if file_path:
            if not file_path.lower().endswith(".xlsx"):
                file_path += ".xlsx"
            self.edit_target_excel.setText(file_path)
            self.log(f"Archivo Excel destino seleccionado: '{file_path}'", "INFO")

    def _browse_master_excel(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Listado Maestro de Participantes",
            "",
            "Libro de Excel (*.xlsx *.xls);;Todos los archivos (*.*)",
        )
        if file_path:
            self.edit_master_excel.setText(file_path)
            self.log(f"Listado maestro seleccionado: '{file_path}'", "INFO")

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    def log(self, message: str, level: str = "INFO") -> None:
        """Append formatted timestamped message to the live console."""
        timestamp = datetime.now(tz=timezone.utc).astimezone().strftime("%H:%M:%S")

        color_map = {
            "INFO": "#93c5fd",       # Light blue
            "SUCCESS": "#34d399",    # Emerald
            "WARNING": "#fbbf24",    # Amber
            "ERROR": "#f87171",      # Rose red
        }
        color = color_map.get(level.upper(), "#e5e7eb")
        badge = f"<b style='color:{color};'>[{level.upper()}]</b>"
        html_entry = f"<span style='color:#6b7280;'>[{timestamp}]</span> {badge} <span style='color:#f3f4f6;'>{message}</span><br>"

        self.console.append(html_entry)
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())
        self.status_bar.showMessage(message)

    def _clear_log(self) -> None:
        self.console.clear()

    # -------------------------------------------------------------------------
    # Table Manipulation
    # -------------------------------------------------------------------------
    def _clear_table(self) -> None:
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self._current_records = []
        self.lbl_table_count.setText("0 filas detectadas")

    def _populate_table(self, records: list[dict[str, Any]]) -> None:
        """Render records into QTableWidget."""
        if not records:
            self._clear_table()
            return

        self._current_records = records

        # Identify all distinct column names preserving appearance order
        col_names: list[str] = []
        for r in records:
            for k in r:
                if k not in col_names:
                    col_names.append(k)

        self.table.setColumnCount(len(col_names))
        self.table.setHorizontalHeaderLabels(col_names)
        self.table.setRowCount(len(records))

        for row_idx, r in enumerate(records):
            for col_idx, col_name in enumerate(col_names):
                val = str(r.get(col_name, ""))
                item = QTableWidgetItem(val)
                self.table.setItem(row_idx, col_idx, item)

        self.lbl_table_count.setText(f"{len(records)} fila(s) detectada(s) | Celdas editables")

    def _get_records_from_table(self) -> list[dict[str, Any]]:
        """Extract user-edited records directly from QTableWidget."""
        row_count = self.table.rowCount()
        col_count = self.table.columnCount()
        if row_count == 0 or col_count == 0:
            return self._current_records

        headers: list[str] = []
        for c in range(col_count):
            header_item = self.table.horizontalHeaderItem(c)
            headers.append(header_item.text() if header_item is not None else f"COL_{c + 1}")
        records: list[dict[str, Any]] = []

        for r in range(row_count):
            row_dict: dict[str, Any] = {}
            for c in range(col_count):
                item = self.table.item(r, c)
                row_dict[headers[c]] = item.text().strip() if item is not None else ""
            records.append(row_dict)

        return records

    def _add_table_row(self) -> None:
        if self.table.columnCount() == 0:
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["DNI", "1 APELLIDO", "2 APELLIDO", "NOMBRE"])

        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        for c in range(self.table.columnCount()):
            self.table.setItem(row_idx, c, QTableWidgetItem(""))
        self.lbl_table_count.setText(f"{self.table.rowCount()} fila(s)")

    def _delete_selected_row(self) -> None:
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
            self.lbl_table_count.setText(f"{self.table.rowCount()} fila(s)")
        else:
            QMessageBox.information(
                self,
                "Selección",
                "Por favor seleccione una fila en la tabla para eliminarla.",
            )

    # -------------------------------------------------------------------------
    # Asynchronous Actions
    # -------------------------------------------------------------------------
    def _set_ui_busy(self, busy: bool) -> None:
        self.btn_analyze.setEnabled(not busy)
        self.btn_validate.setEnabled(not busy)
        self.btn_consolidate.setEnabled(not busy)
        if busy:
            self.setCursor(Qt.CursorShape.WaitCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    # --- 1. Analizar Formulario ---
    def on_analyze_clicked(self) -> None:
        form_path = self.edit_form_path.text().strip()
        if not form_path:
            QMessageBox.warning(
                self,
                "Ruta Requerida",
                "Por favor seleccione la ruta del formulario manuscrito (Imagen o PDF).",
            )
            return

        if not Path(form_path).exists():
            QMessageBox.critical(
                self,
                "Archivo no encontrado",
                f"El archivo especificado no existe:\n{form_path}",
            )
            return

        self._set_ui_busy(True)
        self.progress_bar.setValue(10)

        self._active_worker = OCRWorker(file_path=form_path)
        self._active_worker.sig_log.connect(self.log)
        self._active_worker.sig_progress.connect(self.progress_bar.setValue)
        self._active_worker.sig_finished.connect(self._on_ocr_finished)
        self._active_worker.sig_error.connect(self._on_worker_error)
        self._active_worker.start()

    def _on_ocr_finished(self, records: list[dict[str, Any]]) -> None:
        self._set_ui_busy(False)
        self._populate_table(records)
        QMessageBox.information(
            self,
            "Análisis Completado",
            f"Se detectaron y transcribieron {len(records)} registro(s) desde el formulario.\n"
            "Puede revisar o editar los valores en la tabla antes del siguiente paso.",
        )

    # --- 2. Validar & Enriquecer ---
    def on_validate_clicked(self) -> None:
        records = self._get_records_from_table()
        if not records:
            QMessageBox.warning(
                self,
                "Tabla Vacía",
                "No hay registros en la tabla para validar. Analice un formulario primero o añada filas.",
            )
            return

        target_excel = self.edit_target_excel.text().strip()
        if not target_excel:
            QMessageBox.warning(
                self,
                "Excel Destino Requerido",
                "Por favor especifique la ruta del archivo Excel de destino para validar las cabeceras.",
            )
            return

        master_excel = self.edit_master_excel.text().strip()

        self._set_ui_busy(True)
        self.progress_bar.setValue(10)

        self._active_worker = ValidationWorker(
            records=records,
            target_path=target_excel,
            master_path=master_excel if master_excel else None,
        )
        self._active_worker.sig_log.connect(self.log)
        self._active_worker.sig_progress.connect(self.progress_bar.setValue)
        self._active_worker.sig_finished.connect(self._on_validation_finished)
        self._active_worker.sig_error.connect(self._on_worker_error)
        self._active_worker.start()

    def _on_validation_finished(
        self,
        header_res: HeaderValidationResult,
        fuzzy_res: FuzzyMatchResult | None,
    ) -> None:
        self._set_ui_busy(False)
        if fuzzy_res and fuzzy_res.enriched_records:
            self._populate_table(fuzzy_res.enriched_records)
            msg = (
                f"Validación y Enriquecimiento finalizados:\n\n"
                f"• Esquema Excel: {len(header_res.common_columns)} coincidentes, "
                f"{len(header_res.new_columns)} nuevas columnas.\n"
                f"• Cruce Maestro: {fuzzy_res.matched_count}/{fuzzy_res.total_records} coincidencias exitosas."
            )
        else:
            msg = (
                f"Validación de Cabeceras completada:\n\n"
                f"• Columnas en común: {len(header_res.common_columns)}\n"
                f"• Columnas nuevas: {len(header_res.new_columns)}\n"
                f"• Columnas ausentes en formulario: {len(header_res.missing_columns)}"
            )

        QMessageBox.information(self, "Validación Completada", msg)

    # --- 3. Consolidar en Excel ---
    def on_consolidate_clicked(self) -> None:
        records = self._get_records_from_table()
        if not records:
            QMessageBox.warning(
                self,
                "Tabla Vacía",
                "No hay registros para consolidar.",
            )
            return

        target_excel = self.edit_target_excel.text().strip()
        if not target_excel:
            QMessageBox.warning(
                self,
                "Excel Destino Requerido",
                "Por favor especifique la ruta del archivo Excel de destino.",
            )
            return

        create_if_not_exists = self.cb_create_if_not_exists.isChecked()
        if not Path(target_excel).exists() and not create_if_not_exists:
            QMessageBox.warning(
                self,
                "Archivo No Existe",
                f"El archivo '{target_excel}' no existe y la opción 'Crear nuevo si no existe' está desactivada.",
            )
            return

        self._set_ui_busy(True)
        self.progress_bar.setValue(10)

        self._active_worker = ConsolidationWorker(
            records=records,
            target_path=target_excel,
            create_if_not_exists=create_if_not_exists,
        )
        self._active_worker.sig_log.connect(self.log)
        self._active_worker.sig_progress.connect(self.progress_bar.setValue)
        self._active_worker.sig_finished.connect(self._on_persist_finished)
        self._active_worker.sig_error.connect(self._on_worker_error)
        self._active_worker.start()

    def _on_persist_finished(self, result: PersistResult) -> None:
        self._set_ui_busy(False)
        self.progress_bar.setValue(100)
        QMessageBox.information(
            self,
            "Consolidación Exitosa",
            f"{result.message}\n\nColumnas finales en el archivo:\n{', '.join(result.final_columns)}",
        )

    def _on_worker_error(self, err_message: str) -> None:
        self._set_ui_busy(False)
        self.progress_bar.setValue(0)
        QMessageBox.critical(
            self,
            "Error en la Operación",
            f"Se produjo un error durante el procesamiento:\n\n{err_message}",
        )
