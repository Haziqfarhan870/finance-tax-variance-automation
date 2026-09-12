from __future__ import annotations
import pandas as pd


def _map_dict(config: dict, mode: str) -> dict[str, dict]:
    key = "pnl_accounts" if mode == "PNL" else "bs_accounts"
    return {str(k).lstrip("0"): v for k, v in config[key].items()}


def map_accounts(df: pd.DataFrame, config: dict, mode: str) -> tuple[pd.DataFrame, set[str]]:
    mapping = _map_dict(config, mode)
    out = df.copy()
    out["Mapped"] = out["Account"].isin(mapping)
    out["Level 1"] = out["Account"].map(lambda x: mapping.get(x, {}).get("level1", "UNMAPPED"))
    out["Level 2"] = out["Account"].map(lambda x: mapping.get(x, {}).get("level2", "UNMAPPED"))
    out["Account Name"] = out["Account"].map(lambda x: mapping.get(x, {}).get("name", "Unknown Account"))
    if mode == "PNL":
        mult = out["Account"].map(lambda x: float(mapping.get(x, {}).get("sign_multiplier", 1.0)))
        out["Amount"] = out["Amount"] * mult
    unmapped = set(out.loc[~out["Mapped"], "Account"].unique())
    return out, unmapped
