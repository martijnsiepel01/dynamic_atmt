import yaml
from typing import Dict, Any, Tuple, List
import os

REQUIRED_INTERNAL = {
    "prescriptions": ["patient_id", "patient_contact_id",
                      "start_datetime", "stop_datetime",
                      "medication_name", "prescription_datetime"],
    "cultures":      ["patient_id", "sample_datetime",
                      "material_category"],
    "admissions":    ["patient_id", "patient_contact_id",
                      "admission_start", "admission_end"],
    "order_specifications": ["patient_id", "patient_contact_id",
                             "order_id", "question_id",
                             "answer"],
}

class ConfigurationError(Exception):
    pass

def _split_mapping(source_cfg: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, str]]:
    all_cols = source_cfg["columns"]
    return all_cols.get("required", {}), all_cols.get("optional", {})

def validate_config(cfg: Dict[str, Any]) -> None:
    if "data_sources" not in cfg:
        raise ConfigurationError("Missing data_sources block")

    for src, scfg in cfg["data_sources"].items():
        if not scfg.get("enabled", False):
            continue

        if "file_path" not in scfg:
            raise ConfigurationError(f"{src}: file_path missing")

        if "columns" not in scfg:
            raise ConfigurationError(f"{src}: columns block missing")

        req_map, _ = _split_mapping(scfg)

        missing = [k for k in REQUIRED_INTERNAL.get(src, []) if k not in req_map]
        if missing:
            raise ConfigurationError(
                f"{src}: required mapping(s) not provided: {', '.join(missing)}"
            )

def get_column_mapping(cfg: Dict[str, Any], source: str,
                       include_optional: bool = True) -> Dict[str, str]:
    """Return {internal_name: raw_column_name} for the chosen source."""
    scfg = cfg["data_sources"][source]["columns"]
    mapping = dict(scfg.get("required", {}))
    if include_optional:
        mapping.update(scfg.get("optional", {}))
    return mapping

def get_required_mapping(cfg: Dict[str, Any], source: str) -> Dict[str, str]:
    return cfg["data_sources"][source]["columns"].get("required", {})

def load_config(path: str) -> Dict[str, Any]:
    """Read YAML using UTF-8 first, fall back to latin-1 if needed."""
    if not os.path.exists(path):
        raise ConfigurationError(f"Configuration file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)
    except UnicodeDecodeError:
        # last-resort fallback for ancient files
        with open(path, "r", encoding="latin-1") as fh:
            cfg = yaml.safe_load(fh)

    validate_config(cfg)
    return cfg