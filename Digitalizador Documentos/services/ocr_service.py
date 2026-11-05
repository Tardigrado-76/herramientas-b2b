"""OCR service for LALA application.

Multi-page pipeline:
  1. Load image / render ALL PDF pages.
  2. Per page: detect table region with OpenCV.
  3. Per table cell column: detect and EXCLUDE signature/drawing columns
     (high ink-density, low text confidence → filtered out).
  4. EasyOCR extracts text from the text-only columns of the cropped table.
  5. Geometry-based parser reconstructs rows & columns from bounding boxes.
  6. Results from all pages are merged into one consolidated record list.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, ClassVar

import cv2
import easyocr
import numpy as np
from PIL import Image

try:
    import pymupdf
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

from config import AppConfig

logger = logging.getLogger(__name__)


class OCRError(Exception):
    """Base exception for OCR processing failures."""


class UnsupportedFormatError(OCRError):
    """Raised when an unsupported file format is provided."""


class OCRService:
    """Service to process images/PDFs and extract handwritten form data using local OCR.

    Provider-agnostic and 100% offline. Processes ALL pages of a PDF.
    Detects table regions and excludes signature/drawing columns automatically.
    """

    SUPPORTED_IMAGE_EXTENSIONS: ClassVar[set[str]] = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
    SUPPORTED_EXTENSIONS: ClassVar[set[str]] = SUPPORTED_IMAGE_EXTENSIONS.union({".pdf"})

    # Minimum fraction of image area a table ROI must cover to be considered valid
    MIN_TABLE_AREA_FRACTION = 0.04

    # If a column strip has more than this fraction of dark pixels (ink) vs its area
    # AND its text confidence is low, it is classified as a signature column.
    SIGNATURE_INK_DENSITY_THRESHOLD = 0.08
    # Maximum mean OCR confidence for a column to be classified as a signature column.
    SIGNATURE_MAX_CONFIDENCE = 0.55

    def __init__(self) -> None:
        # Lazy initialization so instantiating OCRService does not write to disk immediately.
        self._reader: Any = None

    @property
    def reader(self) -> Any:
        """Lazy property for EasyOCR Reader instance."""
        if self._reader is None:
            # gpu=False maximises portability; EasyOCR switches to CUDA if torch finds GPU.
            self._reader = easyocr.Reader(["es", "en"], gpu=False)
        return self._reader

    # ------------------------------------------------------------------
    # Image loading helpers
    # ------------------------------------------------------------------
    def _render_pdf_pages(self, pdf_path: Path) -> list[np.ndarray]:
        """Render all pages of a PDF to a list of RGB numpy arrays."""
        if not HAS_PYMUPDF:
            raise OCRError(
                "PyMuPDF no está disponible para renderizar PDFs. "
                "Instale pymupdf o use una imagen (.png, .jpg)."
            )
        try:
            doc = pymupdf.open(pdf_path)
            if doc.page_count < 1:
                raise OCRError("El PDF no contiene páginas legibles.")
            pages = []
            mat = pymupdf.Matrix(2.0, 2.0)   # 2× zoom → ~144 dpi
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                pages.append(np.array(img))
            doc.close()
            logger.info("PDF renderizado: %d página(s).", len(pages))
            return pages
        except OCRError:
            raise
        except Exception as exc:
            raise OCRError(f"Error al procesar el PDF: {exc}") from exc

    def _load_pages(self, file_path: Path) -> list[np.ndarray]:
        """Return a list of RGB numpy arrays (one per page/frame)."""
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            return self._render_pdf_pages(file_path)
        if ext not in self.SUPPORTED_IMAGE_EXTENSIONS:
            raise UnsupportedFormatError(
                f"Formato '{ext}' no compatible. Soportados: "
                f"{', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )
        try:
            with Image.open(file_path) as raw_img:
                img: Image.Image = raw_img.convert("RGB") if raw_img.mode in ("RGBA", "P") else raw_img.copy()
                max_dim = AppConfig.MAX_IMAGE_DIMENSION
                if max(img.size) > max_dim:
                    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
                return [np.array(img)]
        except Exception as exc:
            raise OCRError(f"Error al cargar la imagen: {exc}") from exc

    # ------------------------------------------------------------------
    # Table region detection (OpenCV)
    # ------------------------------------------------------------------
    def _detect_table_region(self, img_np: np.ndarray) -> np.ndarray:
        """Locate the dominant table/grid and return the cropped ROI.

        Uses morphological line detection. Falls back to the full image if no
        structured grid is found.
        """
        h, w = img_np.shape[:2]
        total_area = h * w

        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Horizontal lines
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(30, w // 10), 1))
        h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel, iterations=2)

        # Vertical lines
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(30, h // 10)))
        v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel, iterations=2)

        # Combine and dilate
        grid_mask = cv2.add(h_lines, v_lines)
        dilate_k = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        grid_dilated = cv2.dilate(grid_mask, dilate_k, iterations=3)

        contours, _ = cv2.findContours(
            grid_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            return img_np

        best_rect, best_area = None, 0
        for cnt in contours:
            x, y, cw, ch = cv2.boundingRect(cnt)
            area = cw * ch
            if area > best_area:
                best_area, best_rect = area, (x, y, cw, ch)

        if best_rect is None or best_area < total_area * self.MIN_TABLE_AREA_FRACTION:
            return img_np

        x, y, cw, ch = best_rect
        pad = 10
        x1, y1 = max(0, x - pad), max(0, y - pad)
        x2, y2 = min(w, x + cw + pad), min(h, y + ch + pad)
        return img_np[y1:y2, x1:x2]

    # ------------------------------------------------------------------
    # Signature column detection
    # ------------------------------------------------------------------
    def _detect_column_ranges(self, img_np: np.ndarray) -> list[tuple[int, int]]:
        """Detect vertical column boundaries using the vertical-line mask.

        Returns a list of (x_start, x_end) tuples sorted left→right.
        Falls back to a single full-width range if no separators are found.
        """
        h, w = img_np.shape[:2]
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(20, h // 6)))
        v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel, iterations=2)

        col_profile = np.sum(v_lines, axis=0)  # Sum of white pixels per column
        threshold_line = col_profile.max() * 0.3

        # Identify x-positions of vertical separators
        separator_xs = np.where(col_profile > threshold_line)[0]
        if len(separator_xs) < 2:
            return [(0, w)]

        # Cluster consecutive x positions into separator bands
        separator_bands: list[tuple[int, int]] = []
        band_start = int(separator_xs[0])
        band_end = int(separator_xs[0])
        for x in separator_xs[1:]:
            if x - band_end <= 5:
                band_end = int(x)
            else:
                separator_bands.append((band_start, band_end))
                band_start = band_end = int(x)
        separator_bands.append((band_start, band_end))

        # Column ranges sit between the separator bands
        column_ranges: list[tuple[int, int]] = []
        prev_end = 0
        for sep_start, sep_end in separator_bands:
            if sep_start - prev_end > 20:   # ignore tiny slivers
                column_ranges.append((prev_end, sep_start))
            prev_end = sep_end
        if w - prev_end > 20:
            column_ranges.append((prev_end, w))

        return column_ranges if column_ranges else [(0, w)]

    def _is_signature_column(
        self,
        img_np: np.ndarray,
        x_start: int,
        x_end: int,
        ocr_results: list,
    ) -> bool:
        """Return True if the column strip looks like a signature/drawing column.

        A column is classified as a signature column when:
        - It has high ink density (many dark pixels) BUT
        - The OCR confidence for text blocks inside it is low.

        This handles the common case of handwritten signatures or stamps in form
        columns that should NOT be interpreted as readable text.
        """
        strip = img_np[:, x_start:x_end]
        strip_area = strip.shape[0] * strip.shape[1]
        if strip_area == 0:
            return False

        # Count dark pixels (< 100 brightness on any channel)
        gray_strip = cv2.cvtColor(strip, cv2.COLOR_RGB2GRAY)
        dark_pixels = int(np.sum(gray_strip < 100))
        ink_density = dark_pixels / strip_area

        # Find OCR results whose centre-X falls in this column strip
        col_confidences: list[float] = []
        cx_mid = (x_start + x_end) / 2
        half_w = (x_end - x_start) / 2
        for box, _text, prob in ocr_results:
            xs = [pt[0] for pt in box]
            box_cx = sum(xs) / len(xs)
            if abs(box_cx - cx_mid) < half_w:
                col_confidences.append(float(prob))

        mean_conf = (sum(col_confidences) / len(col_confidences)) if col_confidences else 0.0

        is_sig = (
            ink_density > self.SIGNATURE_INK_DENSITY_THRESHOLD
            and mean_conf < self.SIGNATURE_MAX_CONFIDENCE
        )
        if is_sig:
            logger.debug(
                "Columna [%d-%d] clasificada como FIRMA "
                "(tinta=%.2f%%, conf=%.2f).",
                x_start, x_end, ink_density * 100, mean_conf,
            )
        return is_sig

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def extract_form_data(
        self,
        file_path: str | Path,
        custom_instructions: str | None = None,
    ) -> list[dict[str, Any]]:
        """Detect table regions, exclude signature columns, run EasyOCR on all pages.

        Args:
            file_path: Path to the image or PDF file.
            custom_instructions: Unused; kept for API compatibility.

        Returns:
            Unified list of dicts (all pages merged) with detected column names as keys.
        """
        target_path = Path(file_path).resolve()
        if not target_path.exists():
            raise FileNotFoundError(f"El archivo no existe: {target_path}")

        try:
            pages = self._load_pages(target_path)
            all_records: list[dict[str, Any]] = []

            for page_idx, img_np in enumerate(pages):
                logger.info("Procesando página %d / %d …", page_idx + 1, len(pages))

                # 1. Crop to table region
                table_roi = self._detect_table_region(img_np)

                # 2. Run EasyOCR on the table crop
                raw_results = self.reader.readtext(table_roi)
                if not raw_results:
                    logger.info("Página %d: No se detectó texto en la tabla.", page_idx + 1)
                    continue

                # 3. Detect vertical column ranges in the ROI
                col_ranges = self._detect_column_ranges(table_roi)

                # 4. Identify which column ranges are signature columns → exclude them
                text_col_ranges = [
                    (xs, xe)
                    for xs, xe in col_ranges
                    if not self._is_signature_column(table_roi, xs, xe, raw_results)
                ]

                # 5. Filter OCR results to keep only blocks inside text columns
                filtered_results: list = []
                for item in raw_results:
                    box, _text, _prob = item
                    xs = [pt[0] for pt in box]
                    box_cx = sum(xs) / len(xs)
                    in_text_col = any(xs_start <= box_cx <= xe_end for xs_start, xe_end in text_col_ranges)
                    if in_text_col:
                        filtered_results.append(item)

                # 6. Parse geometry → rows & columns
                page_records = self._parse_easyocr_results(filtered_results)
                if page_records and page_records != [{}]:
                    logger.info(
                        "Página %d: %d registro(s) extraído(s).", page_idx + 1, len(page_records)
                    )
                    all_records.extend(page_records)

            return all_records if all_records else [{}]

        except OCRError:
            raise
        except Exception as exc:
            raise OCRError(f"Fallo en la extracción OCR local: {exc}") from exc

    # ------------------------------------------------------------------
    # Geometry-based table parser
    # ------------------------------------------------------------------
    def _parse_easyocr_results(self, results: list) -> list[dict[str, Any]]:
        """Convert raw EasyOCR bounding boxes into structured tabular data.

        Algorithm:
          1. Compute centre-Y and height of each detected text block.
          2. Group blocks into rows using a Y-tolerance based on median height.
          3. Sort blocks within each row by centre-X.
          4. Treat the topmost row as column headers (must have ≥2 items).
          5. Map every subsequent block to its nearest header column by X distance.
          6. Skip rows that are clearly header/footer text (single-cell full-width rows)
             repeated at the start or contain 'OBSERVACIONES'.
        """
        if not results:
            return [{}]

        items = []
        for box, text, _prob in results:
            text = str(text).strip().upper()
            if not text:
                continue
            xs = [pt[0] for pt in box]
            ys = [pt[1] for pt in box]
            items.append({
                'text': text,
                'cx': sum(xs) / 4.0,
                'cy': sum(ys) / 4.0,
                'h': max(ys) - min(ys),
            })

        if not items:
            return [{}]

        # ── Row grouping ──────────────────────────────────────────────
        items.sort(key=lambda x: x['cy'])
        heights = sorted(item['h'] for item in items)
        median_h = heights[len(heights) // 2]
        row_tolerance = median_h * 0.65

        rows: list[list[dict]] = []
        current_row = [items[0]]
        for item in items[1:]:
            if abs(item['cy'] - current_row[-1]['cy']) < row_tolerance:
                current_row.append(item)
            else:
                rows.append(current_row)
                current_row = [item]
        rows.append(current_row)

        for row in rows:
            row.sort(key=lambda x: x['cx'])

        # ── Single-row fallback ───────────────────────────────────────
        if len(rows) < 2:
            return [{f"COL_{i+1}": item['text'] for i, item in enumerate(rows[0])}]

        # ── Locate header row ─────────────────────────────────────────
        # The header row has ≥ 2 items. Skip any leading single-item rows (title/date lines).
        header_row_idx = 0
        for i, row in enumerate(rows):
            if len(row) >= 2:
                header_row_idx = i
                break

        headers = [item['text'] for item in rows[header_row_idx]]
        header_xs = [item['cx'] for item in rows[header_row_idx]]

        # ── Data rows → records ───────────────────────────────────────
        records: list[dict[str, Any]] = []
        for row in rows[header_row_idx + 1:]:
            # Skip footer rows: single cell spanning wide or containing keywords
            if len(row) == 1:
                text_upper = row[0]['text'].upper()
                if any(kw in text_upper for kw in ('OBSERVACION', 'SUGERENCIA', 'FIRMA', 'PSR-')):
                    continue

            record: dict[str, Any] = {}
            for item in row:
                closest_idx = min(
                    range(len(header_xs)),
                    key=lambda i: abs(item['cx'] - header_xs[i]),
                )
                col_name = headers[closest_idx]
                if col_name in record:
                    record[col_name] += f" {item['text']}"
                else:
                    record[col_name] = item['text']
            if record:
                records.append(record)

        return records or [{}]
