# Financial Reconciliation System

A full-stack application for reconciling Statement and Settlement financial files.

## 🎯 What It Does

This system matches transactions between two files:

- **Statement File** - Company's internal records
- **Settlement File** - Bank/Partner records

And categorizes them into:

- **Category 5** - Present in both files (matched)
- **Category 6** - Only in Settlement file
- **Category 7** - Only in Statement file

---

## 🛠️ Tech Stack

| Layer           | Technology                            |
| --------------- | ------------------------------------- |
| Backend         | Python, FastAPI, Pandas               |
| Frontend        | React, TypeScript, Vite, Tailwind CSS |
| Data Processing | Pandas, NumPy                         |

---

## 📁 Project Structure

```
koshai-assignment/
├── processors/           # Core data processing
│   ├── statement.py      # Statement file processor
│   ├── settlement.py     # Settlement file processor
│   └── reconciler.py     # Matching engine
├── api/
│   └── main.py           # FastAPI REST API
├── frontend/             # React app
│   └── src/
│       ├── App.tsx
│       └── components/
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/koshai-assignment.git
cd koshai-assignment
```

### 2. Start Backend

```bash
pip install -r requirements.txt
python -m uvicorn api.main:app --port 8000
```

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Open Browser

Go to http://localhost:5173

---

## 📖 How It Works

### Statement Processing

1. Removes junk rows (1-9, 11)
2. Extracts 11-digit Partner PIN from descriptions
3. Tags transactions ("Should Reconcile" / "Should Not Reconcile")
4. "Dollar Received" types → Skip
5. Duplicate PINs → Only "Cancel" type reconciles

### Settlement Processing

1. Removes first 2 rows
2. Calculates `estimate_amount_usd = PayoutRoundAmt / APIRate`
3. Tags transactions same as Statement

### Reconciliation

1. Filters for "Should Reconcile" only
2. Outer joins on Partner PIN
3. Categorizes: Both (5), Settlement-only (6), Statement-only (7)
4. Calculates variance for Category 5

---

## 📊 API Endpoints

| Endpoint                  | Method | Description              |
| ------------------------- | ------ | ------------------------ |
| `/api/health`             | GET    | Health check             |
| `/api/reconcile`          | POST   | Upload files & reconcile |
| `/api/process/statement`  | POST   | Process statement only   |
| `/api/process/settlement` | POST   | Process settlement only  |

---
