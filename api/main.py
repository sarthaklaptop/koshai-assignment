# api for reconciliation
# handles file uploads and processing

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
import math

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np

# import our processors
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from processors import (
    process_statement,
    process_settlement,
    reconcile_data,
    generate_reconciliation_report
)

# create app
app = FastAPI(
    title="Reconciliation API",
    description="API for reconciling files",
    version="1.0.0"
)

# cors stuff
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# file types we accept
ALLOWED = {'.csv', '.xlsx', '.xls'}


def check_file(filename):
    """check if file ext is valid"""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED


def save_file(upload_file):
    """save uploaded file to temp"""
    suffix = Path(upload_file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(upload_file.file, tmp)
        return Path(tmp.name)


def clean_val(val):
    """make value json safe"""
    if val is None:
        return None
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return None
        return val
    if isinstance(val, (np.floating, np.integer)):
        val = val.item()
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return None
        return val
    if isinstance(val, np.ndarray):
        return val.tolist()
    if pd.isna(val):
        return None
    return val


def df_to_list(df, limit=None):
    """convert df to list of dicts"""
    if limit:
        df = df.head(limit)
    
    records = df.to_dict(orient='records')
    
    # clean each record
    result = []
    for r in records:
        clean_r = {}
        for k, v in r.items():
            clean_r[k] = clean_val(v)
        result.append(clean_r)
    
    return result


def safe_num(val, default=0.0):
    """make number json safe"""
    if val is None:
        return default
    if math.isnan(val) or math.isinf(val):
        return default
    return round(val, 2)



# health check
@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "service": "Reconciliation API"
    }


# main reconcile endpoint
@app.post("/api/reconcile")
async def reconcile(
    statement_file: UploadFile = File(...),
    settlement_file: UploadFile = File(...),
    limit: int = Query(50),
    statement_amount_col: str = Query("Settle.Amt"),
    settlement_amount_col: str = Query("estimate_amount_usd"),
    settlement_pin_col: str = Query("Partner_Pin"),
    settlement_type_col: str = Query("Type"),
    settlement_payout_col: str = Query("PayoutRoundAmt"),
    settlement_rate_col: str = Query("APIRate")
):
    """main endpoint for reconciling files"""
    
    # check files
    if not check_file(statement_file.filename):
        raise HTTPException(status_code=400, detail=f"bad file type. use: {ALLOWED}")
    
    if not check_file(settlement_file.filename):
        raise HTTPException(status_code=400, detail=f"bad file type. use: {ALLOWED}")
    
    st_path = None
    set_path = None
    
    try:
        # save files
        st_path = save_file(statement_file)
        set_path = save_file(settlement_file)
        
        # process statement
        try:
            st_df = process_statement(st_path)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"statement error: {str(e)}")
        
        # process settlement
        try:
            set_df = process_settlement(
                set_path,
                pin_col=settlement_pin_col,
                type_col=settlement_type_col,
                payout_col=settlement_payout_col,
                rate_col=settlement_rate_col
            )
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"settlement error: {str(e)}")
        
        # reconcile
        try:
            results = reconcile_data(
                st_df, 
                set_df,
                statement_amount_col=statement_amount_col,
                settlement_amount_col=settlement_amount_col
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"reconcile error: {str(e)}")
        
        # build response
        s = results['summary']
        
        return {
            "success": True,
            "message": "done",
            "summary": {
                "total_statement_records": s.total_statement_records,
                "total_settlement_records": s.total_settlement_records,
                "reconcilable_statement": s.reconcilable_statement,
                "reconcilable_settlement": s.reconcilable_settlement,
                "category_5_count": s.category_5_count,
                "category_6_count": s.category_6_count,
                "category_7_count": s.category_7_count,
                "total_variance": safe_num(s.total_variance),
                "avg_variance": safe_num(s.avg_variance),
                "max_variance": safe_num(s.max_variance),
                "min_variance": safe_num(s.min_variance)
            },
            "category_5": df_to_list(results['category_5'], limit),
            "category_6": df_to_list(results['category_6'], limit),
            "category_7": df_to_list(results['category_7'], limit),
            "pagination": {
                "limit": limit,
                "category_5_total": len(results['category_5']),
                "category_6_total": len(results['category_6']),
                "category_7_total": len(results['category_7'])
            }
        }
        
    finally:
        # cleanup
        if st_path and st_path.exists():
            os.unlink(st_path)
        if set_path and set_path.exists():
            os.unlink(set_path)



# process statement only
@app.post("/api/process/statement")
async def proc_statement(file: UploadFile = File(...)):
    """process statement file"""
    
    if not check_file(file.filename):
        raise HTTPException(status_code=400, detail=f"bad file. use: {ALLOWED}")
    
    fpath = None
    
    try:
        fpath = save_file(file)
        
        try:
            df = process_statement(fpath)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"error: {str(e)}")
        
        # stats
        tags = df['Reconcile_Tag'].value_counts().to_dict()
        pins_found = int(df['Partner_Pin'].notna().sum())
        pins_missing = int(df['Partner_Pin'].isna().sum())
        
        return {
            "success": True,
            "message": "done",
            "stats": {
                "total": len(df),
                "pins_found": pins_found,
                "pins_missing": pins_missing,
                "tags": tags
            },
            "columns": df.columns.tolist(),
            "preview": df_to_list(df, 20)
        }
        
    finally:
        if fpath and fpath.exists():
            os.unlink(fpath)


# process settlement only
@app.post("/api/process/settlement")
async def proc_settlement(
    file: UploadFile = File(...),
    pin_col: str = Query("Partner_Pin"),
    type_col: str = Query("Type"),
    payout_col: str = Query("PayoutRoundAmt"),
    rate_col: str = Query("APIRate")
):
    """process settlement file"""
    
    if not check_file(file.filename):
        raise HTTPException(status_code=400, detail=f"bad file. use: {ALLOWED}")
    
    fpath = None
    
    try:
        fpath = save_file(file)
        
        try:
            df = process_settlement(
                fpath,
                pin_col=pin_col,
                type_col=type_col,
                payout_col=payout_col,
                rate_col=rate_col
            )
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"error: {str(e)}")
        
        # stats
        tags = df['Reconcile_Tag'].value_counts().to_dict()
        amt_stats = df['estimate_amount_usd'].describe().to_dict()
        
        return {
            "success": True,
            "message": "done",
            "stats": {
                "total": len(df),
                "tags": tags,
                "amount_stats": {
                    "min": round(amt_stats.get('min', 0), 2),
                    "max": round(amt_stats.get('max', 0), 2),
                    "mean": round(amt_stats.get('mean', 0), 2),
                    "std": round(amt_stats.get('std', 0), 2)
                }
            },
            "columns": df.columns.tolist(),
            "preview": df_to_list(df, 20)
        }
        
    finally:
        if fpath and fpath.exists():
            os.unlink(fpath)


# run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
