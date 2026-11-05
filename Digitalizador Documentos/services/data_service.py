"""Data engine and business logic service for LALA application.

Handles:
- Text normalization via unicodedata (accents, uppercase, punctuation removal).
- Header inspection and schema alignment between extracted forms and target Excel.
- High-performance fuzzy matching via rapidfuzz against reference/master list.
- Safe persistence into Excel files (appending aligned rows or creating new workbooks).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
from rapidfuzz import fuzz

from config import AppConfig


@dataclass
class HeaderValidationResult:
    """Result of comparing extracted form columns against target Excel schema."""

    target_exists: bool
    target_columns: list[str]
    extracted_columns: list[str]
    common_columns: list[str]
    new_columns: list[str]  # In extracted, not in target (will add NaN to old rows)
    missing_columns: list[str]  # In target, not in extracted (will add NaN to new rows)
    is_compatible: bool = True
    messages: list[str] = field(default_factory=list)


@dataclass
class MatchDetail:
    """Detailed record of a single fuzzy match operation."""

    row_index: int
    extracted_identifier: str
    matched_master_name: str
    match_score: float
    field_updates: dict[str, Any]
    status: str  # "MATCHED", "UNMATCHED", "AMBIGUOUS"


@dataclass
class FuzzyMatchResult:
    """Summary of fuzzy enrichment across all records."""

    enriched_records: list[dict[str, Any]]
    total_records: int
    matched_count: int
    unmatched_count: int
    details: list[MatchDetail] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)


@dataclass
class PersistResult:
    """Result of persisting records to target Excel file."""

    target_path: str
    created_new: bool
    rows_added: int
    total_rows: int
    final_columns: list[str]
    message: str


class DataService:
    """Service handling all pandas, unicodedata, rapidfuzz, and Excel operations."""

    @staticmethod
    def normalize_text(text: Any) -> str:
        """Clean and normalize text using unicodedata.

        - Strips leading/trailing whitespace.
        - Removes diacritics and accents (NFKD decomposition).
        - Replaces punctuation with single spaces.
        - Converts to UPPERCASE.
        """
        if pd.isna(text) or text is None:
            return ""

        raw_str = str(text).strip()
        if not raw_str:
            return ""

        # Remove accents/diacritics
        nfkd_form = unicodedata.normalize("NFKD", raw_str)
        only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])

        # Remove commas, dots, special punctuation but preserve alphanumeric and spaces
        cleaned = re.sub(r"[^\w\s-]", " ", only_ascii)
        # Collapse multiple spaces into one
        cleaned = re.sub(r"\s+", " ", cleaned).strip().upper()
        return cleaned

    @classmethod
    def validate_headers(
        cls,
        target_path: str | Path,
        extracted_columns: list[str],
    ) -> HeaderValidationResult:
        """Inspect target Excel file (if exists) and compare schema against extracted columns.

        Args:
            target_path: Path to the target Excel file.
            extracted_columns: List of column names extracted from the form.

        Returns:
            HeaderValidationResult containing comparison details and warnings.
        """
        path = Path(target_path).resolve()
        clean_extracted = [cls.normalize_text(col) for col in extracted_columns if col]

        if not path.exists():
            return HeaderValidationResult(
                target_exists=False,
                target_columns=[],
                extracted_columns=clean_extracted,
                common_columns=[],
                new_columns=clean_extracted,
                missing_columns=[],
                is_compatible=True,
                messages=[
                    (
                        f"El archivo destino '{path.name}' no existe aún. Se creará un nuevo archivo con las columnas: "
                        f"{', '.join(clean_extracted)}."
                    )
                ],
            )

        try:
            # Read only header to be fast and memory-efficient
            df_existing = pd.read_excel(path, nrows=0)
            existing_cols = [str(c).strip() for c in df_existing.columns]
            existing_cols_norm = [cls.normalize_text(c) for c in existing_cols]

            common = [col for col in clean_extracted if col in existing_cols_norm]
            new_cols = [col for col in clean_extracted if col not in existing_cols_norm]
            missing_cols = [col for col in existing_cols_norm if col not in clean_extracted]

            messages: list[str] = []
            if common:
                messages.append(f"Columnas coincidentes ({len(common)}): {', '.join(common)}")
            if new_cols:
                messages.append(
                    f"Columnas nuevas detectadas ({len(new_cols)}): {', '.join(new_cols)} "
                    "(se integrarán al Excel existente con valores vacíos/NaN para filas previas)"
                )
            if missing_cols:
                messages.append(
                    f"Columnas previas no detectadas en el formulario ({len(missing_cols)}): {', '.join(missing_cols)} "
                    "(quedarán con valores vacíos/NaN en los nuevos registros)"
                )

            return HeaderValidationResult(
                target_exists=True,
                target_columns=existing_cols,
                extracted_columns=clean_extracted,
                common_columns=common,
                new_columns=new_cols,
                missing_columns=missing_cols,
                is_compatible=True,
                messages=messages,
            )
        except Exception as e:  # noqa: BLE001
            return HeaderValidationResult(
                target_exists=True,
                target_columns=[],
                extracted_columns=clean_extracted,
                common_columns=[],
                new_columns=clean_extracted,
                missing_columns=[],
                is_compatible=False,
                messages=[f"Error al inspeccionar el archivo de destino: {e}"],
            )

    @classmethod
    def enrich_with_master(
        cls,
        records: list[dict[str, Any]],
        master_path: str | Path,
        threshold: float | None = None,
    ) -> FuzzyMatchResult:
        """Perform fuzzy matching against master participant dataset to auto-complete missing fields.

        Args:
            records: List of extracted form records.
            master_path: Path to the reference/master Excel file.
            threshold: Minimum similarity score (0-100) to accept a match. Defaults to AppConfig.

        Returns:
            FuzzyMatchResult with enriched records and audit log.
        """
        min_score = threshold if threshold is not None else AppConfig.FUZZY_MATCH_THRESHOLD
        logs: list[str] = []

        path = None
        path_exists = False
        if master_path:
            path_str = str(master_path).strip()
            if path_str:
                path = Path(path_str).resolve()
                path_exists = path.exists()

        if not path_exists:
            logs.append("[WARNING] El archivo maestro no existe o no fue especificado. Se aplicará el esquema por defecto.")
            default_cols = ["NOMBRE", "APELLIDOS", "FIRMA"]
            default_records = []
            for _row_idx, r in enumerate(records):
                # Extraer todo el texto de la fila omitiendo keys extrañas
                all_text = " ".join(str(v).strip() for v in r.values() if v)
                all_text = cls.normalize_text(all_text)
                
                clean_record = {col: "" for col in default_cols}
                if all_text:
                    parts = all_text.split()
                    clean_record["NOMBRE"] = parts[0]
                    if len(parts) > 1:
                        clean_record["APELLIDOS"] = " ".join(parts[1:])
                default_records.append(clean_record)

            return FuzzyMatchResult(
                enriched_records=default_records,
                total_records=len(records),
                matched_count=0,
                unmatched_count=len(records),
                logs=logs,
            )

        try:
            df_master = pd.read_excel(path)
        except Exception as e:  # noqa: BLE001
            logs.append(f"[ERROR] No se pudo leer el archivo maestro: {e}")
            return FuzzyMatchResult(
                enriched_records=records,
                total_records=len(records),
                matched_count=0,
                unmatched_count=len(records),
                logs=logs,
            )

        if df_master.empty:
            logs.append("[WARNING] El archivo maestro está vacío.")
            return FuzzyMatchResult(
                enriched_records=records,
                total_records=len(records),
                matched_count=0,
                unmatched_count=len(records),
                logs=logs,
            )

        # Standardize master columns
        master_cols_map = {col: cls.normalize_text(col) for col in df_master.columns}
        df_norm = df_master.rename(columns=master_cols_map)

        # Locate name and DNI/ID candidate columns in master
        name_cols = [c for c in df_norm.columns if any(k in c for k in ("NOMBRE", "PARTICIPANTE", "PERSONA", "ALUMNO", "APELLIDO"))]
        dni_cols = [c for c in df_norm.columns if any(k in c for k in ("DNI", "NIF", "NIE", "IDENTIFICACION", "ID", "DOCUMENTO"))]

        primary_dni_col = dni_cols[0] if dni_cols else None

        # Build master search candidates
        master_records: list[dict[str, Any]] = []
        for idx, row in df_norm.iterrows():
            # Assemble compound name representation
            name_parts = [str(row[c]).strip() for c in name_cols if pd.notna(row[c])]
            compound_name = cls.normalize_text(" ".join(name_parts))
            dni_val = str(row[primary_dni_col]).strip() if primary_dni_col and pd.notna(row[primary_dni_col]) else ""

            master_records.append({
                "index": idx,
                "compound_name": compound_name,
                "dni": dni_val,
                "raw_row": row.to_dict(),
            })

        def _map_unmatched_name(name_str: str, record_out: dict, name_columns: list[str]) -> None:
            if not name_columns or not name_str:
                return
            parts = name_str.split()
            if len(name_columns) == 1:
                record_out[name_columns[0]] = name_str
            elif len(name_columns) == 2:
                record_out[name_columns[0]] = parts[0]
                if len(parts) > 1:
                    record_out[name_columns[1]] = " ".join(parts[1:])
            else:
                record_out[name_columns[0]] = parts[0]
                if len(parts) > 1:
                    record_out[name_columns[1]] = parts[1]
                if len(parts) > 2:
                    record_out[name_columns[2]] = " ".join(parts[2:])

        enriched_records: list[dict[str, Any]] = []
        details: list[MatchDetail] = []
        matched_count = 0
        master_column_list = list(df_norm.columns)

        for row_idx, record in enumerate(records):
            new_record = dict(record)

            # Build query string from record
            # Check for specific name keys
            extracted_name_parts = []
            for k in ("NOMBRE", "1 APELLIDO", "2 APELLIDO", "APELLIDOS", "NOMBRES", "NOMBRE COMPLETO"):
                if new_record.get(k):
                    extracted_name_parts.append(str(new_record[k]))

            # If no specific name keys found, gather text fields that are not DNI/FECHA
            if not extracted_name_parts:
                for k, v in new_record.items():
                    if not any(x in k for x in ("DNI", "ID", "FECHA", "HORA", "FIRMA")) and v:
                        extracted_name_parts.append(str(v))

            query_name = cls.normalize_text(" ".join(extracted_name_parts))
            existing_dni = str(new_record.get("DNI", "")).strip()

            best_match: dict[str, Any] | None = None
            best_score = 0.0

            # 1. Exact or high DNI match first if available
            if existing_dni and primary_dni_col:
                norm_existing_dni = re.sub(r"\W+", "", existing_dni.upper())
                for m in master_records:
                    norm_master_dni = re.sub(r"\W+", "", str(m["dni"]).upper())
                    if norm_existing_dni and norm_master_dni and norm_existing_dni == norm_master_dni:
                        best_match = m
                        best_score = 100.0
                        break

            # 2. Fuzzy match on name if not matched by DNI
            if best_match is None and query_name:
                for m in master_records:
                    target_name = m["compound_name"]
                    if not target_name:
                        continue
                    # Calculate token set ratio and token sort ratio
                    s1 = fuzz.token_set_ratio(query_name, target_name)
                    s2 = fuzz.token_sort_ratio(query_name, target_name)
                    score = max(s1, s2)
                    if score > best_score:
                        best_score = float(score)
                        best_match = m

            # Evaluate match threshold
            clean_record = {col: "" for col in master_column_list}

            if best_match and best_score >= min_score:
                matched_count += 1
                updates: dict[str, Any] = {}

                for master_col in master_column_list:
                    val = best_match["raw_row"].get(master_col, "")
                    val_str = str(val).strip() if pd.notna(val) else ""
                    clean_record[master_col] = val_str
                    updates[master_col] = val_str

                log_msg = (
                    f"Fila {row_idx + 1}: Coincidencia con '{best_match['compound_name']}' "
                    f"(Similitud: {best_score:.1f}%)."
                )
                logs.append(log_msg)

                details.append(
                    MatchDetail(
                        row_index=row_idx,
                        extracted_identifier=query_name or existing_dni,
                        matched_master_name=best_match["compound_name"],
                        match_score=best_score,
                        field_updates=updates,
                        status="MATCHED",
                    )
                )
            else:
                # Map extracted data to master schema for unmatched
                if query_name:
                    _map_unmatched_name(query_name, clean_record, name_cols)
                if existing_dni and primary_dni_col:
                    clean_record[primary_dni_col] = existing_dni

                unmatched_msg = (
                    f"Fila {row_idx + 1}: Sin coincidencia suficiente para '{query_name or existing_dni}' "
                    f"(Mejor puntuación: {best_score:.1f}% < {min_score}% umbral)"
                )
                logs.append(unmatched_msg)
                details.append(
                    MatchDetail(
                        row_index=row_idx,
                        extracted_identifier=query_name or existing_dni,
                        matched_master_name=best_match["compound_name"] if best_match else "",
                        match_score=best_score,
                        field_updates={},
                        status="UNMATCHED",
                    )
                )

            enriched_records.append(clean_record)

        unmatched_count = len(records) - matched_count
        summary_log = (
            f"Proceso de enriquecimiento finalizado: {matched_count}/{len(records)} coincidencias exitosas."
        )
        logs.append(summary_log)

        return FuzzyMatchResult(
            enriched_records=enriched_records,
            total_records=len(records),
            matched_count=matched_count,
            unmatched_count=unmatched_count,
            details=details,
            logs=logs,
        )

    @classmethod
    def persist_to_excel(
        cls,
        records: list[dict[str, Any]],
        target_path: str | Path,
        create_if_not_exists: bool = True,
    ) -> PersistResult:
        """Consolidate records into target Excel spreadsheet.

        If target file exists:
        - Reads existing DataFrame.
        - Dynamically aligns schemas (new columns get NaN for historical rows, missing columns get NaN for new rows).
        - Appends using pd.concat.
        - Persists using openpyxl.

        If target file does not exist:
        - Creates new file if create_if_not_exists is True, otherwise raises FileNotFoundError.

        Args:
            records: List of dictionary records to write.
            target_path: Path to target Excel workbook.
            create_if_not_exists: Allow creating new Excel workbook if absent.

        Returns:
            PersistResult with row counts, column list, and status message.
        """
        if not records:
            raise ValueError("No hay registros para consolidar en el archivo Excel.")

        path = Path(target_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)

        df_new = pd.DataFrame(records)

        # Standardize column headers
        df_new.columns = [str(c).strip().upper() for c in df_new.columns]

        if path.exists():
            try:
                df_existing = pd.read_excel(path)
            except Exception as e:
                raise OSError(f"Error al leer el archivo Excel existente '{path.name}': {e}") from e

            # Standardize existing column names
            df_existing.columns = [str(c).strip().upper() for c in df_existing.columns]

            # Reconcile columns: union of existing and new columns, preserving existing order
            existing_col_order = list(df_existing.columns)
            new_distinct_cols = [c for c in df_new.columns if c not in existing_col_order]
            final_col_order = existing_col_order + new_distinct_cols

            # Reindex to ensure both dataframes have all columns
            df_existing_aligned = df_existing.reindex(columns=final_col_order)
            df_new_aligned = df_new.reindex(columns=final_col_order)

            # Concatenate safely
            df_combined = pd.concat([df_existing_aligned, df_new_aligned], ignore_index=True)
            created_new = False
            rows_added = len(df_new)
            total_rows = len(df_combined)

            try:
                df_combined.to_excel(path, index=False, engine="openpyxl")
            except PermissionError as e:
                raise PermissionError(
                    f"No se puede guardar el archivo '{path.name}'. Está abierto por otro programa. "
                    "Por favor ciérrelo en Excel y vuelva a intentarlo."
                ) from e
            except Exception as e:
                raise OSError(f"Error al guardar los datos en '{path.name}': {e}") from e

            msg = (
                f"Consolidación exitosa: Se agregaron {rows_added} registro(s) a '{path.name}'. "
                f"Total de registros actuales: {total_rows}."
            )
            return PersistResult(
                target_path=str(path),
                created_new=created_new,
                rows_added=rows_added,
                total_rows=total_rows,
                final_columns=final_col_order,
                message=msg,
            )

        # If file does not exist
        if not create_if_not_exists:
            raise FileNotFoundError(
                f"El archivo '{path}' no existe y no está activada la opción 'Crear nuevo si no existe'."
            )

        try:
            df_new.to_excel(path, index=False, engine="openpyxl")
        except PermissionError as e:
            raise PermissionError(
                f"No se tiene permiso de escritura para crear el archivo '{path.name}'."
            ) from e
        except Exception as e:
            raise OSError(f"Error al crear el archivo Excel '{path.name}': {e}") from e

        final_cols = list(df_new.columns)
        rows_added = len(df_new)
        msg = f"Archivo nuevo creado exitosamente: '{path.name}' con {rows_added} registro(s) y {len(final_cols)} columnas."

        return PersistResult(
            target_path=str(path),
            created_new=True,
            rows_added=rows_added,
            total_rows=rows_added,
            final_columns=final_cols,
            message=msg,
        )
