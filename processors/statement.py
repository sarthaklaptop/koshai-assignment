# statement processor
# this file handles statement file processing

import pandas as pd
import re
from pathlib import Path
from typing import Optional, Union


def get_pin(txt):
    """extract pin from text"""
    if pd.isna(txt):
        return None
    
    # regex to find 11 digit number at end
    m = re.search(r'(\d{11})\s*$', str(txt))
    if m:
        return m.group(1)
    return None


def load_statement(fpath):
    """load and clean statement file"""
    fpath = Path(fpath)
    
    # check if excel or csv
    if fpath.suffix.lower() in ['.xlsx', '.xls']:
        data = pd.read_excel(fpath, skiprows=9)
    else:
        data = pd.read_csv(fpath, skiprows=9)
    
    # drop first row (its junk)
    if len(data) > 0:
        data = data.drop(index=0).reset_index(drop=True)
    
    return data



def tag_statement(df):
    """add tags to statement data"""
    
    df = df.copy()
    
    # default all to should reconcile
    df['Reconcile_Tag'] = 'Should Reconcile'
    
    # dollar received should not reconcile
    mask1 = df['Type'].str.strip().str.lower() == 'dollar received'
    df.loc[mask1, 'Reconcile_Tag'] = 'Should Not Reconcile'
    
    # handle duplicates
    counts = df['Partner_Pin'].value_counts()
    dups = counts[counts > 1].index.tolist()
    
    for p in dups:
        if pd.isna(p):
            continue
            
        # mark all as should not reconcile
        m = df['Partner_Pin'] == p
        df.loc[m, 'Reconcile_Tag'] = 'Should Not Reconcile'
        
        # only cancel type should reconcile
        cancel = df['Type'].str.strip().str.lower() == 'cancel'
        df.loc[m & cancel, 'Reconcile_Tag'] = 'Should Reconcile'
    
    return df


def process_statement(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    main fn to process statement file
    does cleaning, pin extraction and tagging
    """
    
    # load file
    df = load_statement(file_path)
    
    # check columns
    required = ['Type', 'PQsTrOptOons']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}. Found: {df.columns.tolist()}")
    
    # get partner pin
    df['Partner_Pin'] = df['PQsTrOptOons'].apply(get_pin)
    
    # add tags
    df = tag_statement(df)
    
    # save processed file
    file_path = Path(file_path)
    out = file_path.with_name(f"{file_path.stem}_processed.xlsx")
    df.to_excel(out, index=False)
    
    return df


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        res = process_statement(sys.argv[1])
        print(f"done! processed {len(res)} rows")
        print(f"\nTags:\n{res['Reconcile_Tag'].value_counts()}")
    else:
        print("usage: python statement.py <file>")
