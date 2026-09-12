import pandas as pd
from src.ingestion import clean_gl

ALIASES={'pstng date':'Posting Date','g/l account':'Account','comp. code':'Company Code','amount in group crcy':'Amount','item text':'Item Text'}

def test_aliases_subtotals_and_dedup():
    df=pd.DataFrame([
        {'Pstng Date':'2026-03-10','G/L Account':'00410100','Comp. Code':'DEMO01','Amount in Group Crcy':100,'Item Text':'A'},
        {'Pstng Date':'2026-03-10','G/L Account':'00410100','Comp. Code':'DEMO01','Amount in Group Crcy':100,'Item Text':'A'},
        {'Pstng Date':'2026-03-31','G/L Account':'','Comp. Code':'','Amount in Group Crcy':None,'Item Text':'Grand Total'},
    ])
    out=clean_gl(df,ALIASES)
    assert len(out)==1
    assert out.iloc[0]['Account']=='410100'
