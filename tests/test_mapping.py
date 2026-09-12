import pandas as pd
from src.mapping import map_accounts

def test_unmapped_detection_and_sign_multiplier():
    cfg={'pnl_accounts':{'100':{'level1':'L1','level2':'L2','name':'Known','sign_multiplier':-1}},'bs_accounts':{}}
    df=pd.DataFrame({'Account':['100','999'],'Amount':[10,5]})
    out,unmapped=map_accounts(df,cfg,'PNL')
    assert out.iloc[0]['Amount']==-10
    assert '999' in unmapped

def test_bs_mapping_does_not_apply_pnl_sign_multiplier():
    cfg={'pnl_accounts':{},'bs_accounts':{'100':{'level1':'L1','level2':'L2','name':'Known','sign_multiplier':-1}}}
    df=pd.DataFrame({'Account':['100'],'Amount':[10]})
    out,_=map_accounts(df,cfg,'BS')
    assert out.iloc[0]['Amount']==10
