from __future__ import annotations
import pandas as pd


def _fmt_m(v: float) -> str:
    if v < 0:
        return f"(${abs(v)/1_000_000:.3f}M)"
    return f"${v/1_000_000:.3f}M"


def build_commentary(metrics: pd.DataFrame, gl_df: pd.DataFrame, quarters: list[str], mode: str, noise: float = 500.0) -> dict[str, tuple[str, str]]:
    d = gl_df.copy()
    d["Year"] = d["Posting Date"].dt.year
    d["Quarter"] = d["Posting Date"].dt.quarter
    d["Quarter Label"] = d["Quarter"].astype(str) + "Q" + d["Year"].astype(str)
    latest, prev = quarters[-1], quarters[-2] if len(quarters) > 1 else quarters[-1]
    results = {}
    for _, row in metrics.iterrows():
        comp, acct = str(row["Company Code"]), str(row["Account"])
        acct_df = d[(d["Company Code"] == comp) & (d["Account"] == acct)]
        lines = []
        if mode == "BS":
            lines += [f"[{latest}] Closing Balance: {_fmt_m(float(row[latest]))}", f"[{prev}] Closing Balance: {_fmt_m(float(row[prev]))}", f"QoQ Movement: {_fmt_m(float(row['Delta QoQ']))}", ""]
        for q in [latest, prev]:
            qdf = acct_df[acct_df["Quarter Label"] == q].copy()
            if qdf.empty:
                lines.append(f"[{q}] No line-item activity")
                continue
            qdf = qdf[qdf["Amount"].abs() >= noise]
            lines.append(f"[{q}] Line items ({len(qdf)} shown):")
            for _, r in qdf.reindex(qdf["Amount"].abs().sort_values(ascending=False).index).head(8).iterrows():
                desc = r.get("Item Text") or r.get("Vendor Name") or r.get("Reference Document") or "(no description)"
                lines.append(f"  {_fmt_m(float(r['Amount']))} — {desc}")
        direction = "increased" if row["Delta QoQ"] > 0 else "decreased" if row["Delta QoQ"] < 0 else "was unchanged"
        insight = f"{row['Account Name']} for entity {comp} {direction} by {_fmt_m(abs(float(row['Delta QoQ'])))} versus {prev}. YTD: {_fmt_m(float(row['YTD']))}."
        results[f"{comp}_{acct}"] = ("\n".join(lines), insight)
    return results
