# reconciler module
# does the matching between statement and settlement

import pandas as pd
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ReconciliationSummary:
    """holds summary stats"""
    total_statement_records: int
    total_settlement_records: int
    reconcilable_statement: int
    reconcilable_settlement: int
    category_5_count: int
    category_6_count: int
    category_7_count: int
    total_variance: float
    avg_variance: float
    max_variance: float
    min_variance: float


def get_reconcilable(df):
    """filter to only reconcilable rows"""
    if 'Reconcile_Tag' not in df.columns:
        raise ValueError("missing Reconcile_Tag column")
    return df[df['Reconcile_Tag'] == 'Should Reconcile'].copy()


def reconcile_data(statement_df, settlement_df,
                   statement_amount_col='Settle.Amt',
                   settlement_amount_col='estimate_amount_usd'):
    """
    main reconciliation function
    matches statement and settlement by Partner_Pin
    
    returns dict with category 5, 6, 7 dataframes and summary
    """
    
    # store counts
    total_st = len(statement_df)
    total_set = len(settlement_df)
    
    # filter for reconcilable only
    st_rec = get_reconcilable(statement_df)
    set_rec = get_reconcilable(settlement_df)
    
    rec_st_cnt = len(st_rec)
    rec_set_cnt = len(set_rec)
    
    
    # rename cols to avoid conflicts
    st_cols = {c: f"st_{c}" for c in st_rec.columns if c != 'Partner_Pin'}
    set_cols = {c: f"set_{c}" for c in set_rec.columns if c != 'Partner_Pin'}
    
    st_merge = st_rec.rename(columns=st_cols)
    set_merge = set_rec.rename(columns=set_cols)
    
    # outer join on partner pin
    merged = pd.merge(st_merge, set_merge, on='Partner_Pin', 
                      how='outer', indicator=True)
    
    # categorize
    # both = cat 5, right_only = cat 6, left_only = cat 7
    merged['Category'] = merged['_merge'].map({
        'both': 5,
        'right_only': 6,
        'left_only': 7
    })
    
    
    # calc variance for cat 5
    st_amt = f"st_{statement_amount_col}"
    set_amt = f"set_{settlement_amount_col}"
    
    merged['Variance'] = None
    merged['Variance_Percent'] = None
    
    cat5_mask = merged['Category'] == 5
    if cat5_mask.any():
        if st_amt in merged.columns and set_amt in merged.columns:
            merged.loc[cat5_mask, 'Variance'] = (
                pd.to_numeric(merged.loc[cat5_mask, set_amt], errors='coerce') -
                pd.to_numeric(merged.loc[cat5_mask, st_amt], errors='coerce')
            )
            
            # percent variance
            st_vals = pd.to_numeric(merged.loc[cat5_mask, st_amt], errors='coerce')
            merged.loc[cat5_mask, 'Variance_Percent'] = (
                merged.loc[cat5_mask, 'Variance'] / st_vals * 100
            ).round(2)
    
    # split by category
    cat5 = merged[merged['Category'] == 5].copy()
    cat6 = merged[merged['Category'] == 6].copy()
    cat7 = merged[merged['Category'] == 7].copy()
    
    # cleanup
    for d in [cat5, cat6, cat7]:
        if '_merge' in d.columns:
            d.drop(columns=['_merge'], inplace=True)
    
    
    # summary stats
    var_vals = cat5['Variance'].dropna()
    
    summary = ReconciliationSummary(
        total_statement_records=total_st,
        total_settlement_records=total_set,
        reconcilable_statement=rec_st_cnt,
        reconcilable_settlement=rec_set_cnt,
        category_5_count=len(cat5),
        category_6_count=len(cat6),
        category_7_count=len(cat7),
        total_variance=float(var_vals.sum()) if len(var_vals) > 0 else 0.0,
        avg_variance=float(var_vals.mean()) if len(var_vals) > 0 else 0.0,
        max_variance=float(var_vals.max()) if len(var_vals) > 0 else 0.0,
        min_variance=float(var_vals.min()) if len(var_vals) > 0 else 0.0
    )
    
    return {
        'category_5': cat5,
        'category_6': cat6,
        'category_7': cat7,
        'summary': summary,
        'all_merged': merged
    }


def generate_reconciliation_report(results):
    """generates text report from results"""
    
    s = results['summary']
    
    # build report string
    report = "\n"
    report = report + "=" * 50 + "\n"
    report = report + "       RECONCILIATION REPORT\n"
    report = report + "=" * 50 + "\n\n"
    
    report = report + "INPUT DATA\n"
    report = report + "-" * 20 + "\n"
    report = report + "Statement Records: " + str(s.total_statement_records) + "\n"
    report = report + "Settlement Records: " + str(s.total_settlement_records) + "\n\n"
    
    report = report + "RECONCILABLE\n"
    report = report + "-" * 20 + "\n"
    report = report + "From Statement: " + str(s.reconcilable_statement) + "\n"
    report = report + "From Settlement: " + str(s.reconcilable_settlement) + "\n\n"
    
    report = report + "RESULTS\n"
    report = report + "-" * 20 + "\n"
    report = report + "Cat 5 (Both): " + str(s.category_5_count) + "\n"
    report = report + "Cat 6 (Settlement only): " + str(s.category_6_count) + "\n"
    report = report + "Cat 7 (Statement only): " + str(s.category_7_count) + "\n\n"
    
    report = report + "VARIANCE\n"
    report = report + "-" * 20 + "\n"
    report = report + "Total: $" + str(round(s.total_variance, 2)) + "\n"
    report = report + "Average: $" + str(round(s.avg_variance, 2)) + "\n"
    report = report + "Max: $" + str(round(s.max_variance, 2)) + "\n"
    report = report + "Min: $" + str(round(s.min_variance, 2)) + "\n"
    
    report = report + "\n" + "=" * 50 + "\n"
    
    return report


if __name__ == "__main__":
    print("reconciler module")
    print("use reconcile_data() to process files")
