from pathlib import Path
import pandas as pd

BASE=Path(__file__).resolve().parents[1]
RAW=BASE/'data'/'raw'

def _write_gl(mode, year, quarter, rows, variant):
    folder=RAW/mode.lower()/str(year); folder.mkdir(parents=True,exist_ok=True)
    df=pd.DataFrame(rows)
    if variant==1:
        ren={'Company Code':'Comp. Code','Account':'G/L Account','Amount':'Amount in Group Crcy'}
    elif variant==2:
        ren={'Company Code':'Company Code','Account':'GL Account','Posting Date':'Pstng Date','Amount':'Amount in Global Currency'}
    else:
        ren={'Company Code':'CoCd','Account':'Account','Amount':'Amount'}
    df=df.rename(columns=ren)
    df.to_excel(folder/f'{mode}_Period_Q{quarter}_{year}.xlsx',index=False)

def main():
    entities=['DEMO01','DEMO02']
    pnl_accounts=['410100','410200','420100','420200']
    bs_accounts=['120100','120200','220100','220200']
    periods=[(2025,4),(2026,1),(2026,2),(2026,3)]
    for i,(year,q) in enumerate(periods,1):
        pnl=[]; bs=[]
        for e_i,e in enumerate(entities,1):
            for a_i,a in enumerate(pnl_accounts,1):
                base=(a_i*1_800_000)+(e_i*450_000)+(i*900_000)
                amt=base if a_i>=3 else -base
                pnl.append({'Posting Date':f'{year}-{q*3:02d}-15','Company Code':e,'Account':a,'Amount':amt,'Item Text':f'Synthetic tax activity {q}Q{year}'})
            # Add one subtotal/spacer row that should be removed
            pnl.append({'Posting Date':f'{year}-{q*3:02d}-28','Company Code':'','Account':'','Amount':None,'Item Text':'Grand Total'})
            for a_i,a in enumerate(bs_accounts,1):
                movement=((a_i*450_000)+(e_i*150_000)+(i*120_000)) * (-1 if a.startswith('22') else 1)
                bs.append({'Posting Date':f'{year}-{q*3:02d}-20','Company Code':e,'Account':a,'Amount':movement,'Item Text':f'Quarter movement {q}Q{year}'})
        # exact duplicate to prove deduplication
        if i==2: pnl.append(dict(pnl[0]))
        _write_gl('PNL',year,q,pnl,(i%3)+1)
        _write_gl('BS',year,q,bs,((i+1)%3)+1)

        tb_folder=RAW/'tb'/str(year); tb_folder.mkdir(parents=True,exist_ok=True)
        tb=[]
        for e_i,e in enumerate(entities,1):
            for a_i,a in enumerate(bs_accounts,1):
                sign=-1 if a.startswith('22') else 1
                bal=sign*((a_i*2_000_000)+(e_i*500_000)+(i*700_000))
                # omit one zero-suppressed style row on purpose
                if not (e=='DEMO02' and a=='120200' and year==2026 and q==2):
                    tb.append({'Company Code':e,'Account':a,'YTD Balance':bal})
        pd.DataFrame(tb).to_excel(tb_folder/f'TB_Q{q}_{year}.xlsx',index=False)
    print(f'Synthetic data written under {RAW}')

if __name__=='__main__': main()
