from __future__ import annotations
import pandas as pd


def quarter_sort_key(label: str) -> tuple[int, int]:
    q, year = label.split("Q")
    return int(year), int(q)


def add_quarter_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Year"] = out["Posting Date"].dt.year
    out["Quarter"] = out["Posting Date"].dt.quarter
    out["Quarter Label"] = out["Quarter"].astype(str) + "Q" + out["Year"].astype(str)
    return out


def _base_index(df: pd.DataFrame) -> pd.DataFrame:
    return df[["Company Code", "Account", "Level 1", "Level 2", "Account Name"]].drop_duplicates()


def build_pnl_pivot(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    d = add_quarter_columns(df)
    quarters = sorted(d["Quarter Label"].unique(), key=quarter_sort_key)
    grouped = d.groupby(["Company Code", "Account", "Level 1", "Level 2", "Account Name", "Quarter Label"], dropna=False)["Amount"].sum().reset_index()
    pivot = grouped.pivot_table(index=["Company Code", "Account", "Level 1", "Level 2", "Account Name"], columns="Quarter Label", values="Amount", aggfunc="sum", fill_value=0.0).reset_index()
    for q in quarters:
        if q not in pivot.columns:
            pivot[q] = 0.0
    return pivot, quarters


def build_bs_pivot(gl_df: pd.DataFrame, tb_df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    d = add_quarter_columns(gl_df)
    gl_quarters = sorted(d["Quarter Label"].unique(), key=quarter_sort_key)
    quarters = sorted(set(gl_quarters) | (set(tb_df["Quarter Label"].unique()) if not tb_df.empty else set()), key=quarter_sort_key)
    base = _base_index(d)
    combos = set(zip(base["Company Code"], base["Account"]))
    if not tb_df.empty:
        combos |= set(zip(tb_df["Company Code"], tb_df["Account"]))
    map_lookup = base.set_index(["Company Code", "Account"]).to_dict("index")
    rows = []
    for comp, acct in sorted(combos):
        info = map_lookup.get((comp, acct), {"Level 1": "UNMAPPED", "Level 2": "UNMAPPED", "Account Name": "Unknown Account"})
        row = {"Company Code": comp, "Account": acct, **info}
        if not tb_df.empty:
            subset = tb_df[(tb_df["Company Code"] == comp) & (tb_df["Account"] == acct)]
            for q in quarters:
                m = subset[subset["Quarter Label"] == q]
                row[q] = float(m["TB Closing Balance"].iloc[0]) if not m.empty else 0.0
        else:
            acct_df = d[(d["Company Code"] == comp) & (d["Account"] == acct)]
            for q in quarters:
                qnum, year = q.split("Q")
                cutoff = int(qnum) * 3
                mask = (acct_df["Year"] < int(year)) | ((acct_df["Year"] == int(year)) & (acct_df["Posting Date"].dt.month <= cutoff))
                row[q] = float(acct_df.loc[mask, "Amount"].sum())
        rows.append(row)
    return pd.DataFrame(rows), quarters


def add_metrics(pivot: pd.DataFrame, quarters: list[str], mode: str, threshold: float) -> pd.DataFrame:
    out = pivot.copy()
    latest = quarters[-1]
    prev = quarters[-2] if len(quarters) > 1 else latest
    out["Delta QoQ"] = out[latest] - out[prev]
    denom = out[prev].abs()
    out["% Change QoQ"] = ((out["Delta QoQ"] / denom) * 100).where(denom >= 100, 0.0)
    current_year = latest.split("Q")[1]
    year_quarters = [q for q in quarters if q.endswith(current_year)]
    out["YTD"] = out[latest] if mode == "BS" else out[year_quarters].sum(axis=1)
    out["Trend"] = "→"
    out.loc[out[latest].round(2) > out[prev].round(2), "Trend"] = "↑"
    out.loc[out[latest].round(2) < out[prev].round(2), "Trend"] = "↓"
    quarter_material = out[quarters].abs().ge(threshold).any(axis=1)
    delta_material = out["Delta QoQ"].abs().ge(threshold)
    out["Materiality"] = (quarter_material | delta_material).map({True: "❗", False: ""})
    return out
