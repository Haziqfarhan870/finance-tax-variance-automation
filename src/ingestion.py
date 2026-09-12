from __future__ import annotations
import logging
import re
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

SUBTOTAL_PATTERNS = [r"^posting per \d+$", r"^period \d+$", r"^subtotal", r"^grand total", r"^total$"]


def normalize_columns(df: pd.DataFrame, aliases: dict[str, str]) -> pd.DataFrame:
    lower = {str(k).strip().lower(): v for k, v in aliases.items()}
    ren = {c: lower[str(c).strip().lower()] for c in df.columns if str(c).strip().lower() in lower}
    return df.rename(columns=ren)


def _is_subtotal_row(row: pd.Series) -> bool:
    acct = row.get("Account")
    comp = row.get("Company Code")
    if pd.isna(acct) or str(acct).strip() == "" or pd.isna(comp) or str(comp).strip() == "":
        return True
    for value in row:
        if pd.notna(value):
            txt = str(value).strip().lower()
            if any(re.match(p, txt, re.I) for p in SUBTOTAL_PATTERNS):
                return True
    return pd.isna(row.get("Amount"))


def clean_gl(df: pd.DataFrame, aliases: dict[str, str]) -> pd.DataFrame:
    df = normalize_columns(df.copy(), aliases)
    required = {"Posting Date", "Account", "Company Code", "Amount"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"GL extract missing columns after normalization: {sorted(missing)}")
    keep_mask = ~df.apply(_is_subtotal_row, axis=1)
    df = df.loc[keep_mask].copy()
    df["Account"] = df["Account"].apply(_clean_key)
    df["Company Code"] = df["Company Code"].apply(_clean_key)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Posting Date"] = pd.to_datetime(df["Posting Date"], errors="coerce")
    for col in ["Item Text", "Vendor Name", "Reference Document", "Document Type"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str).str.strip()
    df = df.dropna(subset=["Posting Date", "Amount"])
    before = len(df)
    df = df.drop_duplicates(keep="first").reset_index(drop=True)
    if before != len(df):
        logger.info("Removed %d exact duplicate rows", before - len(df))
    return df


def _clean_key(v) -> str:
    if pd.isna(v):
        return ""
    s = str(v).strip()
    try:
        s = str(int(float(s)))
    except Exception:
        pass
    return s.lstrip("0") or "0"


def _load_mode_dir(mode_dir: Path, aliases: dict[str, str]) -> pd.DataFrame:
    if not mode_dir.exists():
        return pd.DataFrame()
    frames: list[pd.DataFrame] = []
    for year_dir in sorted([p for p in mode_dir.iterdir() if p.is_dir() and p.name.isdigit()]):
        files = sorted([p for p in year_dir.glob("*.xlsx") if not p.name.startswith("~$") and re.match(r"^(PNL_|BS_)?Period_", p.name, re.I)])
        for path in files:
            frame = clean_gl(pd.read_excel(path), aliases)
            frames.append(frame)
            logger.info("Loaded %s: %d rows", path.name, len(frame))
    return pd.concat(frames, ignore_index=True).drop_duplicates().reset_index(drop=True) if frames else pd.DataFrame()


def load_gl_data(raw_root: Path, mode: str, aliases: dict[str, str]) -> pd.DataFrame:
    return _load_mode_dir(raw_root / mode.lower(), aliases)


def load_tb_data(raw_root: Path) -> pd.DataFrame:
    tb_root = raw_root / "tb"
    if not tb_root.exists():
        return pd.DataFrame()
    frames = []
    for year_dir in sorted([p for p in tb_root.iterdir() if p.is_dir() and p.name.isdigit()]):
        for path in sorted(year_dir.glob("TB_Q*.xlsx")):
            df = pd.read_excel(path)
            required = {"Company Code", "Account", "YTD Balance"}
            missing = required - set(df.columns)
            if missing:
                raise ValueError(f"{path.name} missing TB columns: {sorted(missing)}")
            m = re.search(r"TB_Q(\d)_?(\d{4})", path.stem, re.I)
            if not m:
                raise ValueError(f"Cannot derive quarter from {path.name}")
            q, year = int(m.group(1)), int(m.group(2))
            slim = pd.DataFrame({
                "Company Code": df["Company Code"].apply(_clean_key),
                "Account": df["Account"].apply(_clean_key),
                "TB Closing Balance": pd.to_numeric(df["YTD Balance"], errors="coerce").fillna(0.0),
                "Quarter Label": f"{q}Q{year}",
            })
            frames.append(slim)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
