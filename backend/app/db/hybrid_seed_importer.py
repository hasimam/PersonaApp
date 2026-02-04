"""CSV importer for hybrid self-discovery seed pack."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import (
    AdviceItem,
    AdviceTrigger,
    AppVersion,
    Gene,
    OptionWeight,
    SahabaModel,
    Scenario,
    ScenarioOption,
)


IMPORT_ORDER = [
    "app_versions.csv",
    "genes.csv",
    "scenarios.csv",
    "scenario_options.csv",
    "option_weights.csv",
    "sahaba_models.csv",
    "advice_items.csv",
    "advice_triggers.csv",
]


@dataclass
class CsvRow:
    line_number: int
    values: Dict[str, str]


class SeedImportError(ValueError):
    """Raised when seed import validation fails."""


class _RowErrorBuilder:
    def __init__(self, filename: str):
        self.filename = filename

    def raise_error(self, line_number: int, message: str) -> None:
        raise SeedImportError(f"{self.filename}:{line_number}: {message}")


def _default_seed_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "seed"


def _normalize_optional(raw: str) -> Optional[str]:
    value = raw.strip()
    return value or None


def _parse_required_str(raw: str, field_name: str, err: _RowErrorBuilder, line_number: int) -> str:
    value = raw.strip()
    if not value:
        err.raise_error(line_number, f"missing required field '{field_name}'")
    return value


def _parse_bool(raw: str, field_name: str, err: _RowErrorBuilder, line_number: int) -> bool:
    value = raw.strip().lower()
    if value in {"1", "true", "yes"}:
        return True
    if value in {"0", "false", "no"}:
        return False
    err.raise_error(line_number, f"invalid boolean for '{field_name}': {raw}")
    return False


def _parse_int(raw: str, field_name: str, err: _RowErrorBuilder, line_number: int) -> int:
    value = raw.strip()
    if not value:
        err.raise_error(line_number, f"missing required field '{field_name}'")
    try:
        return int(value)
    except ValueError:
        err.raise_error(line_number, f"invalid integer for '{field_name}': {raw}")
    return 0


def _parse_float(raw: str, field_name: str, err: _RowErrorBuilder, line_number: int) -> float:
    value = raw.strip()
    if not value:
        err.raise_error(line_number, f"missing required field '{field_name}'")
    try:
        return float(value)
    except ValueError:
        err.raise_error(line_number, f"invalid float for '{field_name}': {raw}")
    return 0.0


def _parse_datetime(raw: str, field_name: str, err: _RowErrorBuilder, line_number: int) -> Optional[datetime]:
    value = raw.strip()
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed_date = date.fromisoformat(value)
            return datetime(parsed_date.year, parsed_date.month, parsed_date.day, tzinfo=timezone.utc)
        except ValueError:
            err.raise_error(line_number, f"invalid datetime for '{field_name}': {raw}")

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)

    return parsed


def _read_csv_rows(
    path: Path,
    required_columns: Sequence[str],
    optional_columns: Sequence[str] = (),
    allow_additional_columns: bool = False,
) -> Tuple[List[CsvRow], List[str]]:
    filename = path.name
    err = _RowErrorBuilder(filename)

    if not path.exists():
        raise SeedImportError(f"{filename}: file not found")

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SeedImportError(f"{filename}: missing CSV header")

        header = [name.strip() for name in reader.fieldnames]
        required_set = set(required_columns)
        optional_set = set(optional_columns)
        header_set = set(header)

        missing = [col for col in required_columns if col not in header_set]
        if missing:
            raise SeedImportError(f"{filename}: missing required columns: {', '.join(missing)}")

        if not allow_additional_columns:
            allowed = required_set | optional_set
            unknown = [col for col in header if col not in allowed]
            if unknown:
                raise SeedImportError(f"{filename}: unknown columns: {', '.join(unknown)}")

        rows: List[CsvRow] = []
        for line_number, row in enumerate(reader, start=2):
            normalized = {key.strip(): (value or "") for key, value in row.items()}
            if all(value.strip() == "" for value in normalized.values()):
                continue

            for column in required_columns:
                if normalized.get(column, "").strip() == "":
                    err.raise_error(line_number, f"missing required field '{column}'")

            rows.append(CsvRow(line_number=line_number, values=normalized))

    return rows, header


def _load_existing_single_key(db: Optional[Session], model, column_name: str) -> Set[str]:
    if db is None:
        return set()
    column = getattr(model, column_name)
    return {value for (value,) in db.query(column).all()}


def _load_existing_pair_key(db: Optional[Session], model, first: str, second: str) -> Set[Tuple[str, str]]:
    if db is None:
        return set()
    col_a = getattr(model, first)
    col_b = getattr(model, second)
    return {(a, b) for a, b in db.query(col_a, col_b).all()}


def _load_existing_triple_key(
    db: Optional[Session],
    model,
    first: str,
    second: str,
    third: str,
) -> Set[Tuple[str, str, str]]:
    if db is None:
        return set()
    col_a = getattr(model, first)
    col_b = getattr(model, second)
    col_c = getattr(model, third)
    return {(a, b, c) for a, b, c in db.query(col_a, col_b, col_c).all()}


def _upsert_rows(
    db: Optional[Session],
    model,
    rows: List[Dict[str, object]],
    key_columns: Sequence[str],
    update_columns: Sequence[str],
) -> None:
    if db is None or not rows:
        return

    stmt = pg_insert(model.__table__).values(rows)
    set_map = {column: getattr(stmt.excluded, column) for column in update_columns}
    db.execute(stmt.on_conflict_do_update(index_elements=list(key_columns), set_=set_map))


def import_hybrid_seed_pack(seed_dir: Optional[Path] = None, dry_run: bool = False) -> Dict[str, int]:
    """Import hybrid seed CSVs into content tables in strict order."""
    seed_path = seed_dir or _default_seed_dir()

    if dry_run:
        return _import_hybrid_seed_pack(db=None, seed_path=seed_path)

    db = SessionLocal()
    try:
        summary = _import_hybrid_seed_pack(db=db, seed_path=seed_path)
        db.commit()
        return summary
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _import_hybrid_seed_pack(db: Optional[Session], seed_path: Path) -> Dict[str, int]:
    summary: Dict[str, int] = {}

    # 1) app_versions.csv
    app_rows, _ = _read_csv_rows(
        seed_path / "app_versions.csv",
        required_columns=["version_id", "name", "is_active", "published_at"],
        optional_columns=["notes"],
    )
    app_err = _RowErrorBuilder("app_versions.csv")
    app_payload: List[Dict[str, object]] = []
    version_ids = _load_existing_single_key(db, AppVersion, "version_id")

    for row in app_rows:
        version_id = _parse_required_str(row.values["version_id"], "version_id", app_err, row.line_number)
        app_payload.append(
            {
                "version_id": version_id,
                "name": _parse_required_str(row.values["name"], "name", app_err, row.line_number),
                "is_active": _parse_bool(row.values["is_active"], "is_active", app_err, row.line_number),
                "published_at": _parse_datetime(
                    row.values["published_at"],
                    "published_at",
                    app_err,
                    row.line_number,
                ),
                "notes": _normalize_optional(row.values.get("notes", "")),
            }
        )
        version_ids.add(version_id)

    _upsert_rows(
        db,
        AppVersion,
        app_payload,
        key_columns=["version_id"],
        update_columns=["name", "is_active", "published_at", "notes"],
    )
    summary["app_versions"] = len(app_payload)

    # 2) genes.csv
    gene_rows, gene_header = _read_csv_rows(
        seed_path / "genes.csv",
        required_columns=["gene_code", "name_en", "desc_en"],
        optional_columns=["version_id", "name_ar", "desc_ar"],
    )
    gene_err = _RowErrorBuilder("genes.csv")
    gene_has_version = "version_id" in gene_header

    if not gene_has_version and len(version_ids) != 1:
        raise SeedImportError(
            "genes.csv:1: missing 'version_id' column is only supported when exactly one app version exists"
        )

    default_version_id = next(iter(version_ids)) if not gene_has_version else None
    gene_keys = _load_existing_pair_key(db, Gene, "version_id", "gene_code")
    gene_payload: List[Dict[str, object]] = []

    for row in gene_rows:
        version_id = (
            _parse_required_str(row.values["version_id"], "version_id", gene_err, row.line_number)
            if gene_has_version
            else default_version_id
        )
        assert version_id is not None
        if version_id not in version_ids:
            gene_err.raise_error(row.line_number, f"unknown version_id '{version_id}'")

        gene_code = _parse_required_str(row.values["gene_code"], "gene_code", gene_err, row.line_number)
        gene_payload.append(
            {
                "version_id": version_id,
                "gene_code": gene_code,
                "name_en": _parse_required_str(row.values["name_en"], "name_en", gene_err, row.line_number),
                "name_ar": _normalize_optional(row.values.get("name_ar", "")),
                "desc_en": _parse_required_str(row.values["desc_en"], "desc_en", gene_err, row.line_number),
                "desc_ar": _normalize_optional(row.values.get("desc_ar", "")),
            }
        )
        gene_keys.add((version_id, gene_code))

    _upsert_rows(
        db,
        Gene,
        gene_payload,
        key_columns=["version_id", "gene_code"],
        update_columns=["name_en", "name_ar", "desc_en", "desc_ar"],
    )
    summary["genes"] = len(gene_payload)

    # 3) scenarios.csv
    scenario_rows, _ = _read_csv_rows(
        seed_path / "scenarios.csv",
        required_columns=["version_id", "scenario_code", "order_index", "scenario_text_en"],
        optional_columns=["scenario_set_code", "scenario_text_ar"],
    )
    scenario_err = _RowErrorBuilder("scenarios.csv")
    scenario_keys = _load_existing_pair_key(db, Scenario, "version_id", "scenario_code")
    scenario_payload: List[Dict[str, object]] = []

    for row in scenario_rows:
        version_id = _parse_required_str(row.values["version_id"], "version_id", scenario_err, row.line_number)
        if version_id not in version_ids:
            scenario_err.raise_error(row.line_number, f"unknown version_id '{version_id}'")

        scenario_code = _parse_required_str(
            row.values["scenario_code"], "scenario_code", scenario_err, row.line_number
        )
        scenario_payload.append(
            {
                "version_id": version_id,
                "scenario_code": scenario_code,
                "scenario_set_code": _normalize_optional(row.values.get("scenario_set_code", "")) or "default",
                "order_index": _parse_int(
                    row.values["order_index"], "order_index", scenario_err, row.line_number
                ),
                "scenario_text_en": _parse_required_str(
                    row.values["scenario_text_en"],
                    "scenario_text_en",
                    scenario_err,
                    row.line_number,
                ),
                "scenario_text_ar": _normalize_optional(row.values.get("scenario_text_ar", "")),
            }
        )
        scenario_keys.add((version_id, scenario_code))

    _upsert_rows(
        db,
        Scenario,
        scenario_payload,
        key_columns=["version_id", "scenario_code"],
        update_columns=["scenario_set_code", "order_index", "scenario_text_en", "scenario_text_ar"],
    )
    summary["scenarios"] = len(scenario_payload)

    # 4) scenario_options.csv
    option_rows, _ = _read_csv_rows(
        seed_path / "scenario_options.csv",
        required_columns=["version_id", "scenario_code", "option_code", "option_text_en"],
        optional_columns=["option_text_ar"],
    )
    option_err = _RowErrorBuilder("scenario_options.csv")
    scenario_option_keys = _load_existing_triple_key(
        db,
        ScenarioOption,
        "version_id",
        "scenario_code",
        "option_code",
    )
    option_payload: List[Dict[str, object]] = []

    for row in option_rows:
        version_id = _parse_required_str(row.values["version_id"], "version_id", option_err, row.line_number)
        scenario_code = _parse_required_str(
            row.values["scenario_code"], "scenario_code", option_err, row.line_number
        )
        if (version_id, scenario_code) not in scenario_keys:
            option_err.raise_error(
                row.line_number,
                f"unknown scenario reference ({version_id}, {scenario_code})",
            )

        option_code = _parse_required_str(row.values["option_code"], "option_code", option_err, row.line_number)
        option_payload.append(
            {
                "version_id": version_id,
                "scenario_code": scenario_code,
                "option_code": option_code,
                "option_text_en": _parse_required_str(
                    row.values["option_text_en"], "option_text_en", option_err, row.line_number
                ),
                "option_text_ar": _normalize_optional(row.values.get("option_text_ar", "")),
            }
        )
        scenario_option_keys.add((version_id, scenario_code, option_code))

    _upsert_rows(
        db,
        ScenarioOption,
        option_payload,
        key_columns=["version_id", "scenario_code", "option_code"],
        update_columns=["option_text_en", "option_text_ar"],
    )
    summary["scenario_options"] = len(option_payload)

    # 5) option_weights.csv
    weight_rows, _ = _read_csv_rows(
        seed_path / "option_weights.csv",
        required_columns=["version_id", "scenario_code", "option_code", "gene_code", "weight"],
    )
    weight_err = _RowErrorBuilder("option_weights.csv")
    weight_payload: List[Dict[str, object]] = []

    for row in weight_rows:
        version_id = _parse_required_str(row.values["version_id"], "version_id", weight_err, row.line_number)
        scenario_code = _parse_required_str(
            row.values["scenario_code"], "scenario_code", weight_err, row.line_number
        )
        option_code = _parse_required_str(row.values["option_code"], "option_code", weight_err, row.line_number)
        gene_code = _parse_required_str(row.values["gene_code"], "gene_code", weight_err, row.line_number)

        if (version_id, scenario_code, option_code) not in scenario_option_keys:
            weight_err.raise_error(
                row.line_number,
                f"unknown option reference ({version_id}, {scenario_code}, {option_code})",
            )
        if (version_id, gene_code) not in gene_keys:
            weight_err.raise_error(row.line_number, f"unknown gene reference ({version_id}, {gene_code})")

        weight_payload.append(
            {
                "version_id": version_id,
                "scenario_code": scenario_code,
                "option_code": option_code,
                "gene_code": gene_code,
                "weight": _parse_float(row.values["weight"], "weight", weight_err, row.line_number),
            }
        )

    _upsert_rows(
        db,
        OptionWeight,
        weight_payload,
        key_columns=["version_id", "scenario_code", "option_code", "gene_code"],
        update_columns=["weight"],
    )
    summary["option_weights"] = len(weight_payload)

    # 6) sahaba_models.csv
    model_rows, model_header = _read_csv_rows(
        seed_path / "sahaba_models.csv",
        required_columns=["version_id", "model_code", "name_en"],
        optional_columns=["name_ar", "summary_ar"],
        allow_additional_columns=True,
    )
    model_err = _RowErrorBuilder("sahaba_models.csv")
    model_base_columns = {"version_id", "model_code", "name_en", "name_ar", "summary_ar"}
    model_gene_columns = [column for column in model_header if column not in model_base_columns]

    if not model_gene_columns:
        raise SeedImportError("sahaba_models.csv:1: expected at least one gene vector column")

    model_keys = _load_existing_pair_key(db, SahabaModel, "version_id", "model_code")
    model_payload: List[Dict[str, object]] = []

    for row in model_rows:
        version_id = _parse_required_str(row.values["version_id"], "version_id", model_err, row.line_number)
        if version_id not in version_ids:
            model_err.raise_error(row.line_number, f"unknown version_id '{version_id}'")

        version_gene_codes = {gene for row_version, gene in gene_keys if row_version == version_id}
        if not version_gene_codes:
            model_err.raise_error(row.line_number, f"no genes loaded for version '{version_id}'")

        missing_gene_columns = sorted(version_gene_codes - set(model_gene_columns))
        if missing_gene_columns:
            model_err.raise_error(
                row.line_number,
                f"missing gene vector columns for version '{version_id}': {', '.join(missing_gene_columns)}",
            )

        unknown_gene_columns = sorted(
            column
            for column in model_gene_columns
            if (version_id, column) not in gene_keys
        )
        if unknown_gene_columns:
            model_err.raise_error(
                row.line_number,
                f"unknown gene columns for version '{version_id}': {', '.join(unknown_gene_columns)}",
            )

        gene_vector = {
            gene_code: _parse_float(row.values[gene_code], gene_code, model_err, row.line_number)
            for gene_code in sorted(version_gene_codes)
        }

        model_code = _parse_required_str(row.values["model_code"], "model_code", model_err, row.line_number)
        model_payload.append(
            {
                "version_id": version_id,
                "model_code": model_code,
                "name_en": _parse_required_str(row.values["name_en"], "name_en", model_err, row.line_number),
                "name_ar": _normalize_optional(row.values.get("name_ar", "")),
                "summary_ar": _normalize_optional(row.values.get("summary_ar", "")),
                "gene_vector_jsonb": gene_vector,
            }
        )
        model_keys.add((version_id, model_code))

    _upsert_rows(
        db,
        SahabaModel,
        model_payload,
        key_columns=["version_id", "model_code"],
        update_columns=["name_en", "name_ar", "summary_ar", "gene_vector_jsonb"],
    )
    summary["sahaba_models"] = len(model_payload)

    # 7) advice_items.csv
    advice_rows, _ = _read_csv_rows(
        seed_path / "advice_items.csv",
        required_columns=[
            "version_id",
            "advice_id",
            "channel",
            "advice_type",
            "title_en",
            "body_en",
            "priority",
        ],
        optional_columns=["title_ar", "body_ar"],
    )
    advice_err = _RowErrorBuilder("advice_items.csv")
    advice_keys = _load_existing_pair_key(db, AdviceItem, "version_id", "advice_id")
    advice_payload: List[Dict[str, object]] = []

    for row in advice_rows:
        version_id = _parse_required_str(row.values["version_id"], "version_id", advice_err, row.line_number)
        if version_id not in version_ids:
            advice_err.raise_error(row.line_number, f"unknown version_id '{version_id}'")

        advice_id = _parse_required_str(row.values["advice_id"], "advice_id", advice_err, row.line_number)
        advice_payload.append(
            {
                "version_id": version_id,
                "advice_id": advice_id,
                "channel": _parse_required_str(row.values["channel"], "channel", advice_err, row.line_number),
                "advice_type": _parse_required_str(
                    row.values["advice_type"], "advice_type", advice_err, row.line_number
                ),
                "title_en": _parse_required_str(
                    row.values["title_en"], "title_en", advice_err, row.line_number
                ),
                "title_ar": _normalize_optional(row.values.get("title_ar", "")),
                "body_en": _parse_required_str(row.values["body_en"], "body_en", advice_err, row.line_number),
                "body_ar": _normalize_optional(row.values.get("body_ar", "")),
                "priority": _parse_int(row.values["priority"], "priority", advice_err, row.line_number),
            }
        )
        advice_keys.add((version_id, advice_id))

    _upsert_rows(
        db,
        AdviceItem,
        advice_payload,
        key_columns=["version_id", "advice_id"],
        update_columns=["channel", "advice_type", "title_en", "title_ar", "body_en", "body_ar", "priority"],
    )
    summary["advice_items"] = len(advice_payload)

    # 8) advice_triggers.csv
    trigger_rows, _ = _read_csv_rows(
        seed_path / "advice_triggers.csv",
        required_columns=[
            "version_id",
            "trigger_id",
            "trigger_type",
            "channel",
            "advice_id",
            "min_score",
            "max_score",
        ],
        optional_columns=["gene_code", "model_code"],
    )
    trigger_err = _RowErrorBuilder("advice_triggers.csv")
    trigger_payload: List[Dict[str, object]] = []

    for row in trigger_rows:
        version_id = _parse_required_str(row.values["version_id"], "version_id", trigger_err, row.line_number)
        if version_id not in version_ids:
            trigger_err.raise_error(row.line_number, f"unknown version_id '{version_id}'")

        advice_id = _parse_required_str(row.values["advice_id"], "advice_id", trigger_err, row.line_number)
        if (version_id, advice_id) not in advice_keys:
            trigger_err.raise_error(row.line_number, f"unknown advice reference ({version_id}, {advice_id})")

        gene_code = _normalize_optional(row.values.get("gene_code", ""))
        model_code = _normalize_optional(row.values.get("model_code", ""))

        if gene_code and (version_id, gene_code) not in gene_keys:
            trigger_err.raise_error(row.line_number, f"unknown gene reference ({version_id}, {gene_code})")
        if model_code and (version_id, model_code) not in model_keys:
            trigger_err.raise_error(row.line_number, f"unknown model reference ({version_id}, {model_code})")

        min_score = _parse_float(row.values["min_score"], "min_score", trigger_err, row.line_number)
        max_score = _parse_float(row.values["max_score"], "max_score", trigger_err, row.line_number)
        if min_score > max_score:
            trigger_err.raise_error(row.line_number, "min_score must be less than or equal to max_score")

        trigger_payload.append(
            {
                "version_id": version_id,
                "trigger_id": _parse_required_str(
                    row.values["trigger_id"], "trigger_id", trigger_err, row.line_number
                ),
                "trigger_type": _parse_required_str(
                    row.values["trigger_type"], "trigger_type", trigger_err, row.line_number
                ),
                "gene_code": gene_code,
                "model_code": model_code,
                "channel": _parse_required_str(row.values["channel"], "channel", trigger_err, row.line_number),
                "advice_id": advice_id,
                "min_score": min_score,
                "max_score": max_score,
            }
        )

    _upsert_rows(
        db,
        AdviceTrigger,
        trigger_payload,
        key_columns=["version_id", "trigger_id"],
        update_columns=[
            "trigger_type",
            "gene_code",
            "model_code",
            "channel",
            "advice_id",
            "min_score",
            "max_score",
        ],
    )
    summary["advice_triggers"] = len(trigger_payload)

    return summary


def _format_summary(summary: Dict[str, int]) -> str:
    ordered_parts = [f"{filename.replace('.csv', '')}={summary.get(filename.replace('.csv', ''), 0)}" for filename in IMPORT_ORDER]
    return ", ".join(ordered_parts)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Import hybrid self-discovery seed CSV pack")
    parser.add_argument(
        "--seed-dir",
        type=Path,
        default=_default_seed_dir(),
        help="Path to seed directory (defaults to repo seed/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and parse all CSV files without committing to the database",
    )

    args = parser.parse_args(argv)
    summary = import_hybrid_seed_pack(seed_dir=args.seed_dir, dry_run=args.dry_run)

    mode = "validated" if args.dry_run else "imported"
    print(f"Hybrid seed pack {mode}: {_format_summary(summary)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
