from __future__ import annotations
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
from .config_loader import load_config
from .ingestion import load_gl_data, load_tb_data
from .mapping import map_accounts
from .analysis import build_pnl_pivot, build_bs_pivot, add_metrics
from .commentary import build_commentary
from .report_writer import write_report

logger=logging.getLogger(__name__)


def run(base_dir: Path) -> Path:
    cfg=load_config(base_dir/"config"/"portfolio_config.yaml")
    raw=base_dir/"data"/"raw"
    pnl_raw=load_gl_data(raw,"PNL",cfg["column_aliases"])
    bs_raw=load_gl_data(raw,"BS",cfg["column_aliases"])
    tb=load_tb_data(raw)
    if pnl_raw.empty and bs_raw.empty:
        raise RuntimeError("No PNL or BS data found. Run the synthetic-data generator first.")
    threshold=float(cfg["materiality_threshold"])
    pnl_metrics=pd.DataFrame(); bs_metrics=pd.DataFrame(); pnl_q=[]; bs_q=[]; pnl_comments={}; bs_comments={}
    if not pnl_raw.empty:
        pnl_map,unmapped=map_accounts(pnl_raw,cfg,"PNL"); logger.info("PNL unmapped accounts: %s",sorted(unmapped) if unmapped else "none")
        pivot,pnl_q=build_pnl_pivot(pnl_map); pnl_metrics=add_metrics(pivot,pnl_q,"PNL",threshold); pnl_comments=build_commentary(pnl_metrics,pnl_map,pnl_q,"PNL")
    if not bs_raw.empty:
        bs_map,unmapped=map_accounts(bs_raw,cfg,"BS"); logger.info("BS unmapped accounts: %s",sorted(unmapped) if unmapped else "none")
        pivot,bs_q=build_bs_pivot(bs_map,tb); bs_metrics=add_metrics(pivot,bs_q,"BS",threshold); bs_comments=build_commentary(bs_metrics,bs_map,bs_q,"BS")
    output=base_dir/"data"/"output"/f"Tax_Variance_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    write_report(pnl_metrics,pnl_q,pnl_comments,bs_metrics,bs_q,bs_comments,output)
    logger.info("Report written: %s",output)
    return output
