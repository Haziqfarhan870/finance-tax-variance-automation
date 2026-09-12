from __future__ import annotations
from pathlib import Path
import yaml


def load_config(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    if not isinstance(cfg, dict):
        raise ValueError("Configuration must be a mapping")
    for key in ["column_aliases", "pnl_accounts", "bs_accounts", "materiality_threshold"]:
        if key not in cfg:
            raise ValueError(f"Missing config key: {key}")
    return cfg
