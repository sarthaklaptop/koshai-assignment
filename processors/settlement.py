# settlement file processor
# handles settlement files for reconciliation

import pandas as pd
from pathlib import Path
from typing import Optional, Union

def load_settlement(fpath):
    """loads settlement file and cleans it"""
    fpath = Path(fpath)
    
    if fpath.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(fpath, skiprows=2)
    else:
        df = pd.read_csv(fpath, skiprows=2)
    return df


def calc_usd_amount(df, payout_col='PayoutRoundAmt', rate_col='APIRate'):
    """
    calculates usd amount from payout and rate
    formula: payout / rate = usd
    """
    df = df.copy()
    
    # convert to numbers
    df[payout_col] = pd.to_numeric(df[payout_col], errors='coerce')
    df[rate_col] = pd.to_numeric(df[rate_col], errors='coerce')
    
    # calculate usd amt
    def calc(row):
        if row[rate_col] != 0:
            return row[payout_col] / row[rate_col]
        return None
    
    df['estimate_amount_usd'] = df.apply(calc, axis=1)
    return df



def tag_settlement(df, pin_col='Partner_Pin', type_col='Type'):
    """adds reconcile tags to settlement"""
    
    df = df.copy()
    df['Reconcile_Tag'] = 'Should Reconcile'
    
    # find duplicate pins
    cnts = df[pin_col].value_counts()
    dups = cnts[cnts > 1].index.tolist()
    
    for pin in dups:
        if pd.isna(pin):
            continue
        
        msk = df[pin_col] == pin
        df.loc[msk, 'Reconcile_Tag'] = 'Should Not Reconcile'
        
        # cancel type should reconcile
        cancel_msk = df[type_col].str.strip().str.lower() == 'cancel'
        df.loc[msk & cancel_msk, 'Reconcile_Tag'] = 'Should Reconcile'
    
    return df


def process_settlement(file_path: Union[str, Path],
                       pin_col: str = 'Partner_Pin',
                       type_col: str = 'Type',
                       payout_col: str = 'PayoutRoundAmt',
                       rate_col: str = 'APIRate') -> pd.DataFrame:
    """
    processes settlement file
    - loads and cleans
    - calculates usd amount  
    - adds tags
    """
    
    df = load_settlement(file_path)
    
    # validate cols exist
    req_cols = [pin_col, type_col, payout_col, rate_col]
    missing = [c for c in req_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Found: {df.columns.tolist()}")
    
    # calc usd
    df = calc_usd_amount(df, payout_col, rate_col)
    
    # tagging
    df = tag_settlement(df, pin_col, type_col)
    
    # rename pin col if needed
    if pin_col != 'Partner_Pin':
        df = df.rename(columns={pin_col: 'Partner_Pin'})
    
    return df



if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = process_settlement(sys.argv[1])
        print(f"processed {len(result)} records")
        print(f"\nTags:\n{result['Reconcile_Tag'].value_counts()}")
    else:
        print("usage: python settlement.py <file>")
