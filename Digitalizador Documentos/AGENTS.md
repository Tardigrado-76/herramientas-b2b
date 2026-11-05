# LALA — Agent Instructions

## Project Overview

Desktop OCR application (PySide6) that extracts handwritten form data from images/PDFs, enriches records via fuzzy matching, and consolidates into Excel. Spanish-language UI.

## Quick Commands

```bash
# Run the application
python main.py

# Run tests
pytest tests/ -v

# Generate sample data (creates files in sample_data/)
python -m sample_data.generate_samples
```

## Architecture

- `main.py` — Entry point, initializes PySide6 QApplication
- `gui/` — PySide6 GUI (main_window, worker threads, styles)
- `services/ocr_service.py` — Local OCR pipeline: OpenCV table detection → EasyOCR → geometry parser
- `services/data_service.py` — Text normalization, header validation, rapidfuzz matching, Excel persistence
- `config.py` — App constants (name, version, fuzzy threshold 72%, max image dimension 2048)
- `sample_data/` — Demo files (master list, target Excel, simulated form image)

## Key Behaviors

- OCR is **100% local** (EasyOCR + OpenCV), no cloud API calls despite `.env.example`
- Text normalization: strips diacritics, removes punctuation, uppercases (unicodedata NFKD)
- Table detection: morphological line-grid detection, falls back to full image if no grid found
- Fuzzy matching uses rapidfuzz `token_set_ratio` and `token_sort_ratio`, threshold 72%
- Excel persistence dynamically aligns schemas (new columns get NaN for old rows, missing columns get NaN for new rows)
- All UI text and error messages are in Spanish

## Testing

Tests cover: text normalization, header validation, fuzzy matching, Excel persistence, OCR geometry parsing, table region detection. Uses `pytest` with `tmp_path` fixtures. No external services required.

## Dependencies

PySide6, pandas, openpyxl, rapidfuzz, easyocr, pillow, pymupdf, python-dotenv, opencv-python (via easyocr)
