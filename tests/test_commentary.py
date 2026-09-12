import pandas as pd
from src.commentary import build_commentary

def test_commentary_mentions_movement():
    metrics=pd.DataFrame([{'Company Code':'E1','Account':'1','Account Name':'Tax','1Q2026':1000,'2Q2026':1500,'Delta QoQ':500,'YTD':2500}])
    gl=pd.DataFrame([{'Posting Date':pd.Timestamp('2026-06-01'),'Company Code':'E1','Account':'1','Amount':1500,'Item Text':'Adjustment','Vendor Name':'','Reference Document':''}])
    out=build_commentary(metrics,gl,['1Q2026','2Q2026'],'PNL',noise=0)
    assert 'increased' in out['E1_1'][1]
