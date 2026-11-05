"""Unit tests for LALA application services.

Tests DataService normalization, header validation, fuzzy matching,
persistence, OCR response standardization, lazy initialization, signature
column filtering, and edge cases.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pandas as pd
import pytest

from gui.worker import ConsolidationWorker, OCRWorker, ValidationWorker
from services.data_service import DataService
from services.ocr_service import OCRError, OCRService, UnsupportedFormatError


@pytest.fixture(autouse=True)
def mock_easyocr_reader() -> Iterator[MagicMock]:
    """Mock easyocr.Reader globally so tests never touch disk or download models."""
    with patch("easyocr.Reader") as mock_reader:
        mock_instance = MagicMock()
        mock_reader.return_value = mock_instance
        yield mock_instance


def test_normalize_text() -> None:
    """Test unicodedata text cleaning and diacritic removal."""
    assert DataService.normalize_text("  José Mª Pérez  ") == "JOSE MA PEREZ"
    assert DataService.normalize_text("Ángel Núñez-González") == "ANGEL NUNEZ-GONZALEZ"
    assert DataService.normalize_text("12.345.678-K") == "12 345 678-K"
    assert DataService.normalize_text(None) == ""
    assert DataService.normalize_text(float("nan")) == ""


def test_normalize_text_edge_cases() -> None:
    """Test edge cases for normalize_text with symbols, whitespace, and numbers."""
    assert DataService.normalize_text("   \n\t  ") == ""
    assert DataService.normalize_text("¡Hola, @Mundo! #2026$") == "HOLA MUNDO 2026"
    assert DataService.normalize_text("Ñandú Pingüino Çedilla") == "NANDU PINGUINO CEDILLA"
    assert DataService.normalize_text(123456) == "123456"


def test_validate_headers(tmp_path: Path) -> None:
    """Test header inspection against target Excel workbook."""
    target = tmp_path / "test_target.xlsx"

    # Non-existent target
    res1 = DataService.validate_headers(target, ["DNI", "NOMBRE", "FECHA"])
    assert not res1.target_exists
    assert "DNI" in res1.new_columns

    # Create target with existing schema
    df_existing = pd.DataFrame([{"DNI": "123", "NOMBRE": "ANA", "TURNO": "MANANA"}])
    df_existing.to_excel(target, index=False, engine="openpyxl")

    # Existent target with partial overlap
    res2 = DataService.validate_headers(target, ["DNI", "NOMBRE", "FIRMA"])
    assert res2.target_exists
    assert "DNI" in res2.common_columns
    assert "NOMBRE" in res2.common_columns
    assert "FIRMA" in res2.new_columns
    assert "TURNO" in res2.missing_columns


def test_enrich_with_master(tmp_path: Path) -> None:
    """Test rapidfuzz participant matching and field autocompletion."""
    master_file = tmp_path / "master.xlsx"
    master_data = [
        {"DNI": "12345678A", "NOMBRES": "JOSE MORALES CANAZO", "TELEFONO": "600111222"},
        {"DNI": "23456789B", "NOMBRES": "PEDRO PEREZ CARRASCOSA", "TELEFONO": "600222333"},
    ]
    pd.DataFrame(master_data).to_excel(master_file, index=False, engine="openpyxl")

    # Form records with missing DNI and slight variation in name
    extracted_records = [
        {"NOMBRE": "Jose", "1 APELLIDO": "Morales", "2 APELLIDO": "Canazo", "DNI": ""},
        {"NOMBRE": "Pedro Perez Carrascosa", "DNI": ""},
        {"NOMBRE": "Desconocido Total", "DNI": ""},
    ]

    enrich_res = DataService.enrich_with_master(
        records=extracted_records,
        master_path=master_file,
        threshold=70.0,
    )

    assert enrich_res.matched_count == 2
    assert enrich_res.unmatched_count == 1

    # Check auto-filled fields
    rec1 = enrich_res.enriched_records[0]
    assert rec1["DNI"] == "12345678A"
    assert rec1["TELEFONO"] == "600111222"

    rec2 = enrich_res.enriched_records[1]
    assert rec2["DNI"] == "23456789B"


def test_enrich_without_master_file(tmp_path: Path) -> None:
    """Test fallback enrichment when no master file exists."""
    missing_master = tmp_path / "nonexistent_master.xlsx"
    records = [{"COL_1": "Juan Carlos Gomez"}]
    res = DataService.enrich_with_master(records, missing_master)
    assert res.matched_count == 0
    assert res.unmatched_count == 1
    assert res.enriched_records[0]["NOMBRE"] == "JUAN"
    assert res.enriched_records[0]["APELLIDOS"] == "CARLOS GOMEZ"


def test_enrich_exact_dni_match(tmp_path: Path) -> None:
    """Test exact DNI match overrides slight name differences."""
    master_file = tmp_path / "master_dni.xlsx"
    master_data = [
        {"DNI": "12345678-Z", "NOMBRE": "MARIA LUISA", "APELLIDOS": "FERNANDEZ"},
    ]
    pd.DataFrame(master_data).to_excel(master_file, index=False, engine="openpyxl")

    records = [{"DNI": "12345678Z", "NOMBRE": "M. Luisa"}]
    res = DataService.enrich_with_master(records, master_file, threshold=85.0)
    assert res.matched_count == 1
    assert res.details[0].match_score == 100.0
    assert res.enriched_records[0]["APELLIDOS"] == "FERNANDEZ"


def test_persist_to_excel_new_and_append(tmp_path: Path) -> None:
    """Test creating a new workbook and subsequently appending aligned rows."""
    dest_path = tmp_path / "consolidated.xlsx"

    # 1. Create brand new file
    initial_records = [
        {"DNI": "11111111A", "NOMBRE": "ALICIA", "ROL": "ADMIN"}
    ]
    res1 = DataService.persist_to_excel(initial_records, dest_path, create_if_not_exists=True)
    assert res1.created_new
    assert res1.rows_added == 1
    assert res1.total_rows == 1
    assert Path(dest_path).exists()

    # 2. Append new records with additional columns
    new_records = [
        {"DNI": "22222222B", "NOMBRE": "BERNARDO", "TURNO": "TARDE"}
    ]
    res2 = DataService.persist_to_excel(new_records, dest_path)
    assert not res2.created_new
    assert res2.rows_added == 1
    assert res2.total_rows == 2

    # Verify saved workbook content
    df_final = pd.read_excel(dest_path)
    assert len(df_final) == 2
    assert "DNI" in df_final.columns
    assert "NOMBRE" in df_final.columns
    assert "ROL" in df_final.columns
    assert "TURNO" in df_final.columns
    # Alicia should have NaN/empty TURNO, Bernardo should have NaN/empty ROL
    assert pd.isna(df_final.loc[0, "TURNO"])
    assert pd.isna(df_final.loc[1, "ROL"])


def test_persist_to_excel_errors(tmp_path: Path) -> None:
    """Test error conditions in persist_to_excel."""
    dest_path = tmp_path / "missing.xlsx"
    with pytest.raises(ValueError, match="No hay registros"):
        DataService.persist_to_excel([], dest_path)

    with pytest.raises(FileNotFoundError):
        DataService.persist_to_excel([{"A": "1"}], dest_path, create_if_not_exists=False)


def test_ocr_lazy_initialization(mock_easyocr_reader: MagicMock) -> None:
    """Verify OCRService does not instantiate easyocr.Reader until .reader is accessed."""
    ocr_service = OCRService()
    assert ocr_service._reader is None
    # Accessing .reader triggers lazy initialization
    reader_obj = ocr_service.reader
    assert reader_obj is mock_easyocr_reader
    assert ocr_service._reader is mock_easyocr_reader


def test_ocr_parse_geometry() -> None:
    """Test dynamic geometry-based parsing of EasyOCR results."""
    ocr_service = OCRService()

    # Mock EasyOCR result format: [(box, text, prob), ...]
    mock_results = [
        ([[10, 10], [40, 10], [40, 30], [10, 30]], "DNI", 0.99),
        ([[100, 10], [150, 10], [150, 30], [100, 30]], "NOMBRE", 0.98),
        ([[12, 50], [42, 50], [42, 70], [12, 70]], "12345", 0.95),
        ([[98, 50], [130, 50], [130, 70], [98, 70]], "ANA", 0.92),
    ]

    records = ocr_service._parse_easyocr_results(mock_results)

    assert len(records) == 1
    assert records[0]["DNI"] == "12345"
    assert records[0]["NOMBRE"] == "ANA"


def test_ocr_signature_column_detection() -> None:
    """Test GDPR signature column detection based on ink density and low OCR confidence."""
    ocr_service = OCRService()
    # Create a 100x200 image where x=100..200 has dark signature strokes (>8% dark pixels)
    img = np.full((100, 200, 3), 255, dtype=np.uint8)
    img[20:60, 120:180] = 10  # Dark ink block in second column (40*60 = 2400 / 10000 = 24% density)

    low_conf_results = [
        ([[130, 25], [170, 25], [170, 55], [130, 55]], "scribble", 0.20),
    ]
    assert ocr_service._is_signature_column(img, 100, 200, low_conf_results) is True
    assert ocr_service._is_signature_column(img, 0, 100, low_conf_results) is False


def test_ocr_unsupported_format(tmp_path: Path) -> None:
    """Test UnsupportedFormatError and FileNotFoundError on invalid files."""
    ocr_service = OCRService()
    with pytest.raises(FileNotFoundError):
        ocr_service.extract_form_data(tmp_path / "nonexistent.png")

    bad_file = tmp_path / "bad.txt"
    bad_file.write_text("hello", encoding="utf-8")
    with pytest.raises(UnsupportedFormatError):
        ocr_service.extract_form_data(bad_file)


def test_table_region_detection() -> None:
    """Verify that _detect_table_region crops to the grid and ignores surrounding text."""
    ocr_service = OCRService()

    h_img, w_img = 400, 600
    img = np.full((h_img, w_img, 3), 255, dtype=np.uint8)

    # Draw a simple 4-column × 2-row grid centred in the image
    table_x, table_y = 100, 150
    cell_w, cell_h = 100, 60
    cols, rows_n = 4, 2

    for r in range(rows_n + 1):
        y = table_y + r * cell_h
        cv2.line(img, (table_x, y), (table_x + cols * cell_w, y), (0, 0, 0), 2)

    for c in range(cols + 1):
        x = table_x + c * cell_w
        cv2.line(img, (x, table_y), (x, table_y + rows_n * cell_h), (0, 0, 0), 2)

    # Draw some "header text" outside the table at the very top (y < 50)
    cv2.putText(
        img,
        "INFORME DE ASISTENCIA 2024",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2,
    )

    roi = ocr_service._detect_table_region(img)

    roi_area = roi.shape[0] * roi.shape[1]
    full_area = h_img * w_img

    # The ROI should be smaller than 80% of the full image
    assert roi_area < full_area * 0.80, (
        f"Expected ROI smaller than 80% of full image, got {roi_area / full_area:.1%}"
    )
    # The ROI should cover at least MIN_TABLE_AREA_FRACTION of the image
    assert roi_area >= full_area * OCRService.MIN_TABLE_AREA_FRACTION


def test_workers_execution(tmp_path: Path) -> None:
    """Test background worker classes synchronously via .run()."""
    target_xlsx = tmp_path / "worker_out.xlsx"
    records = [{"DNI": "99999999X", "NOMBRE": "TEST WORKER"}]

    val_worker = ValidationWorker(records=records, target_path=str(target_xlsx))
    val_worker.run()

    cons_worker = ConsolidationWorker(records=records, target_path=str(target_xlsx))
    cons_worker.run()
    assert target_xlsx.exists()

    ocr_worker = OCRWorker(file_path=str(tmp_path / "missing_img.png"))
    ocr_worker.run()  # Should catch error gracefully and emit sig_error without raising
    assert not isinstance(ocr_worker, OCRError)
