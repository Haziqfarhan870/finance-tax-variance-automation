import pandas as pd
from src.analysis import build_pnl_pivot, build_bs_pivot, add_metrics


def _gl():
    return pd.DataFrame([
        {'Posting Date':pd.Timestamp('2026-03-01'),'Company Code':'E1','Account':'1','Level 1':'L1','Level 2':'L2','Account Name':'A','Amount':100},
        {'Posting Date':pd.Timestamp('2026-06-01'),'Company Code':'E1','Account':'1','Level 1':'L1','Level 2':'L2','Account Name':'A','Amount':150},
    ])

def test_pnl_ytd_is_sum_of_current_year_quarters():
    p,q=build_pnl_pivot(_gl()); m=add_metrics(p,q,'PNL',1000)
    assert m.iloc[0]['YTD']==250
    assert m.iloc[0]['Delta QoQ']==50

def test_bs_uses_tb_closing_balance_and_ytd_latest():
    tb=pd.DataFrame([{'Company Code':'E1','Account':'1','TB Closing Balance':1000,'Quarter Label':'1Q2026'},{'Company Code':'E1','Account':'1','TB Closing Balance':1400,'Quarter Label':'2Q2026'}])
    p,q=build_bs_pivot(_gl(),tb); m=add_metrics(p,q,'BS',10000)
    assert m.iloc[0]['1Q2026']==1000
    assert m.iloc[0]['2Q2026']==1400
    assert m.iloc[0]['YTD']==1400
    assert m.iloc[0]['Delta QoQ']==400

def test_bs_missing_tb_row_is_zero_when_tb_exists():
    tb=pd.DataFrame([{'Company Code':'E1','Account':'1','TB Closing Balance':1000,'Quarter Label':'1Q2026'}])
    p,q=build_bs_pivot(_gl(),tb)
    assert p.iloc[0]['2Q2026']==0

def test_materiality_can_trigger_from_quarter_balance():
    p,q=build_pnl_pivot(_gl()); m=add_metrics(p,q,'PNL',120)
    assert m.iloc[0]['Materiality']=='❗'


def test_pct_change_uses_absolute_prior_period_denominator():
    df=pd.DataFrame([
        {'Posting Date':pd.Timestamp('2026-03-01'),'Company Code':'E1','Account':'1','Level 1':'L1','Level 2':'L2','Account Name':'A','Amount':-200},
        {'Posting Date':pd.Timestamp('2026-06-01'),'Company Code':'E1','Account':'1','Level 1':'L1','Level 2':'L2','Account Name':'A','Amount':-300},
    ])
    p,q=build_pnl_pivot(df); m=add_metrics(p,q,'PNL',99999)
    assert round(float(m.iloc[0]['% Change QoQ']),1)==-50.0


def test_bs_gl_fallback_is_cumulative_when_tb_absent():
    p,q=build_bs_pivot(_gl(),pd.DataFrame())
    assert p.iloc[0]['1Q2026']==100
    assert p.iloc[0]['2Q2026']==250
