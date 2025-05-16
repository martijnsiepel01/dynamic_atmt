# src/core/data_processor.py
"""
A fully dynamic version of DataProcessor.

*   **Mandatory** columns for each source are enforced at load-time
    (see `config_loader.get_required_mapping()`).
*   Every other column is considered **optional** and will be passed
    straight through to the JSON output – no code changes needed when
    you add or remove optional columns in *config.yaml*.

The only fields that are *never* copied to the JSON are the ones used
purely for internal housekeeping (listed in `ALWAYS_IGNORE`).
"""

from __future__ import annotations

import json
import datetime as _dt
from typing import Dict, Any, Optional, List, Set

import pandas as pd
from pandas import Timestamp
from datetime import timedelta

from .config_loader import (
    get_column_mapping,
    get_required_mapping,
    ConfigurationError,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _is_dt(x) -> bool:
    return isinstance(x, (Timestamp, _dt.datetime))


def _fmt_dt(x) -> Optional[str]:
    """Format Timestamp → str, keep None/NaT as None, leave others intact."""
    if pd.isna(x):
        return None
    if _is_dt(x):
        return x.strftime("%Y-%m-%d %H:%M:%S")
    return x


def _row_to_dict(row: pd.Series, ignore: Set[str] | None = None) -> Dict[str, Any]:
    """
    Convert a Series to a JSON-ready dict, keeping *all* non-NA columns
    except those in *ignore*.
    """
    ignore = ignore or set()
    out: Dict[str, Any] = {}
    for col, val in row.items():
        if col in ignore or pd.isna(val):
            continue
        out[col] = _fmt_dt(val)
    return out


# House-keeping columns that should never leak to JSON
ALWAYS_IGNORE: Set[str] = {
    "group",  # internal treatment group id
}

# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------


class DataProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_sources: Dict[str, pd.DataFrame] = {}
        self.load_data_sources()

    # --------------------------------------------------------------------- #
    # 1) LOAD & VALIDATE DATA
    # --------------------------------------------------------------------- #

    def load_data_sources(self) -> None:
        for src, scfg in self.config["data_sources"].items():
            if not scfg.get("enabled", False):
                continue

            df = pd.read_csv(scfg["file_path"], encoding="utf-8", low_memory=False)

            # 1) rename *only* the columns defined in the mapping
            mapping = get_column_mapping(self.config, src)      # req + opt
            df = df.rename(columns={v: k for k, v in mapping.items()})

            # 2) 🚫 throw away every other column
            allowed_cols = set(mapping.keys())                  # internal names
            df = df.loc[:, df.columns.isin(allowed_cols)].copy()

            # 3) enforce mandatory columns are present
            req_cols = list(get_required_mapping(self.config, src).keys())
            missing = [c for c in req_cols if c not in df.columns]
            if missing:
                raise ConfigurationError(
                    f"{src}: file {scfg['file_path']} misses required column(s): "
                    f"{', '.join(missing)}"
                )

            # 4) parse *_datetime columns that survived the trim-down
            for col in [c for c in df.columns if c.endswith("_datetime")]:
                df[col] = pd.to_datetime(df[col], errors="coerce")

            self.data_sources[src] = df

    # --------------------------------------------------------------------- #
    # 2) PUBLIC ENTRY POINT
    # --------------------------------------------------------------------- #

    def process_data(self) -> Dict[str, Any]:
        """
        Orchestrate the full processing flow and return the final nested dict.
        """
        prescriptions_df = self.data_sources["prescriptions"]
        result: Dict[str, Any] = {}

        for patient_id, pt_df in prescriptions_df.groupby("patient_id"):
            admissions: List[Dict[str, Any]] = []

            # group by admission / encounter
            for adm_id, adm_df in pt_df.groupby("patient_contact_id"):
                adm_df = self._create_treatment_groups(adm_df)
                admissions.append(self._process_admission(adm_id, adm_df))

            result[str(patient_id)] = {"admissions": admissions}

        return result

    # --------------------------------------------------------------------- #
    # 3) ADMISSION / TREATMENT / PRESCRIPTION
    # --------------------------------------------------------------------- #

    def _create_treatment_groups(self, df: pd.DataFrame) -> pd.DataFrame:
        """Group overlapping prescriptions (24 h gap rule)."""
        if df.empty:
            return df

        df = df.sort_values("start_datetime")
        groups: List[int] = []
        curr_group = 0
        curr_end = df.iloc[0]["stop_datetime"]

        for _, row in df.iterrows():
            if (
                pd.notna(row["start_datetime"])
                and pd.notna(curr_end)
                and row["start_datetime"] > curr_end + pd.Timedelta(hours=24)
            ):
                curr_group += 1
            curr_end = max(curr_end, row["stop_datetime"])
            groups.append(curr_group)

        df = df.copy()
        df["group"] = groups
        return df

    # ------------------------

    def _process_admission(self, adm_id: str, adm_df: pd.DataFrame) -> Dict[str, Any]:
        info = self._get_admission_info(adm_id)
        treatments: List[Dict[str, Any]] = []

        for grp_id, grp_df in adm_df.groupby("group"):
            treatments.append(self._process_treatment(grp_id, grp_df))

        return {
            "patient_contact_id": adm_id,
            "admission_start": _fmt_dt(info.get("admission_start")),
            "admission_end": _fmt_dt(info.get("admission_end")),
            "treatments": treatments,
        }

    # ------------------------

    def _get_admission_info(self, adm_id: str) -> Dict[str, Any]:
        if "admissions" not in self.data_sources:
            return {}
        adm_df = self.data_sources["admissions"]
        m = adm_df[adm_df["patient_contact_id"] == adm_id]
        return m.iloc[0].to_dict() if not m.empty else {}

    # ------------------------

    def _process_treatment(self, grp_id: int, grp_df: pd.DataFrame) -> Dict[str, Any]:
        t_start = grp_df["start_datetime"].min()
        t_end = grp_df["stop_datetime"].max()

        prescriptions = [
            self._process_prescription(row) for _, row in grp_df.iterrows()
        ]

        first = grp_df.sort_values("start_datetime").iloc[0]
        window_cfg = self.config["analysis_options"]["culture_time_windows"]
        win = (
            window_cfg["intra_abdominal"]
            if self._is_intra_abdominal(first)
            else window_cfg["default"]
        )

        cultures = self._find_relevant_cultures(
            patient_id=first["patient_id"],
            anchor=first["start_datetime"],
            hrs_before=win["hours_before"],
            hrs_after=win["hours_after"],
        )

        return {
            "treatment_id": int(grp_id),
            "treatment_start": _fmt_dt(t_start),
            "treatment_end": _fmt_dt(t_end),
            "prescriptions": prescriptions,
            "treatment_cultures": cultures,
        }

    # ------------------------

    def _process_prescription(self, row: pd.Series) -> Dict[str, Any]:
        result = _row_to_dict(row, ignore=ALWAYS_IGNORE)

        # Attach order specifications (if any)
        specs = self._get_order_specifications(
            row["patient_id"], row["patient_contact_id"], row.get("order_id")
        )
        if specs:
            result["order_specifications"] = specs

        return result

    # --------------------------------------------------------------------- #
    # 4) ORDER SPECIFICATIONS & CULTURES
    # --------------------------------------------------------------------- #

    def _get_order_specifications(
        self, patient_id: str, patient_contact_id: str, order_id: str | None
    ) -> List[Dict[str, Any]]:
        if (
            "order_specifications" not in self.data_sources
            or not self.config["data_sources"]["order_specifications"]["enabled"]
            or order_id is None
        ):
            return []

        df = self.data_sources["order_specifications"]
        specs = df[
            (df["patient_id"] == patient_id)
            & (df["patient_contact_id"] == patient_contact_id)
            & (df["order_id"] == order_id)
        ]

        return [_row_to_dict(r, ignore=set()) for _, r in specs.iterrows()]

    # ------------------------

    def _find_relevant_cultures(
        self,
        patient_id: str,
        anchor: Timestamp,
        hrs_before: int,
        hrs_after: int,
    ) -> List[Dict[str, Any]]:
        if "cultures" not in self.data_sources or pd.isna(anchor):
            return []

        cdf = self.data_sources["cultures"]
        t0 = anchor - timedelta(hours=hrs_before)
        t1 = anchor + timedelta(hours=hrs_after)

        rel = cdf[
            (cdf["patient_id"] == patient_id)
            & (cdf["sample_datetime"] >= t0)
            & (cdf["sample_datetime"] <= t1)
        ].sort_values("sample_datetime")

        # de-duplicate on a minimal composite key
        seen = set()
        out: List[Dict[str, Any]] = []
        for _, row in rel.iterrows():
            key = (
                row.get("ordernummer"),
                row.get("sample_datetime"),
                row.get("material_category"),
                row.get("culture_result"),
            )
            if key in seen:
                continue
            seen.add(key)
            out.append(_row_to_dict(row, ignore=set()))

        return out

    # --------------------------------------------------------------------- #
    # 5) UTILITY
    # --------------------------------------------------------------------- #

    def _is_intra_abdominal(self, row: pd.Series) -> bool:
        """
        Very specific business rule: check order_specifications for the phrase
        'intra-abdominale infectie'.
        """
        specs = self._get_order_specifications(
            row["patient_id"], row["patient_contact_id"], row.get("order_id")
        )
        for s in specs:
            if "answer" in s and "intra-abdominale infectie" in str(s["answer"]).lower():
                return True
        return False

    # --------------------------------------------------------------------- #
    # 6) SAVE
    # --------------------------------------------------------------------- #

    def save_output(self, result: Dict[str, Any]) -> None:
        path = self.config["output"]["file_path"]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=4, ensure_ascii=False)
