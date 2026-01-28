import { useState } from "react";
import { FileUpload } from "./components/FileUpload";
import { SummaryCards } from "./components/SummaryCards";
import { CategoryTabs } from "./components/CategoryTabs";
import { reconcileFiles, type ReconciliationResponse } from "./api";

type AppState = "idle" | "loading" | "results" | "error";

function App() {
  const [statementFile, setStatementFile] = useState<File | null>(null);
  const [settlementFile, setSettlementFile] = useState<File | null>(null);
  const [appState, setAppState] = useState<AppState>("idle");
  const [results, setResults] = useState<ReconciliationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canReconcile = statementFile !== null && settlementFile !== null;

  // handles the reconciliation process
  const handleReconcile = async () => {
    if (!statementFile || !settlementFile) return;

    console.log("Sending files:", {
      statement: statementFile.name,
      settlement: settlementFile.name,
    });

    setAppState("loading");
    setError(null);

    try {
      const response = await reconcileFiles(statementFile, settlementFile);
      setResults(response);
      setAppState("results");
    } catch (err: unknown) {
      console.error("Reconciliation error:", err);

      // try to get error message from response
      let errorMessage =
        "Failed to reconcile files. Make sure the API server is running.";
      if (err && typeof err === "object" && "response" in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        if (axiosErr.response?.data?.detail) {
          errorMessage = axiosErr.response.data.detail;
        }
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }

      setError(errorMessage);
      setAppState("error");
    }
  };

  // resets the app to initial state
  const handleReset = () => {
    setStatementFile(null);
    setSettlementFile(null);
    setResults(null);
    setError(null);
    setAppState("idle");
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-slate-800">
                Financial Reconciliation
              </h1>
              <p className="text-sm text-slate-500">
                Statement & Settlement Matcher
              </p>
            </div>
            {appState === "results" && (
              <button
                onClick={handleReset}
                className="px-4 py-2 text-sm text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-md transition-colors"
              >
                New Reconciliation
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 py-8">
        {/* Upload State */}
        {(appState === "idle" || appState === "error") && (
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-lg font-medium text-slate-700 mb-1">
                Upload Your Files
              </h2>
              <p className="text-slate-500 text-sm">
                Select both Statement and Settlement files to begin
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md text-red-600 text-sm">
                <strong>Error:</strong> {error}
              </div>
            )}

            {/* File Upload Zone */}
            <div className="flex flex-col md:flex-row gap-4 mb-6">
              <FileUpload
                label="Statement File"
                file={statementFile}
                onFileSelect={setStatementFile}
              />
              <FileUpload
                label="Settlement File"
                file={settlementFile}
                onFileSelect={setSettlementFile}
              />
            </div>

            {/* Reconcile Button */}
            <button
              onClick={handleReconcile}
              disabled={!canReconcile}
              className={`w-full py-3 rounded-md font-medium text-white transition-colors
                ${
                  canReconcile
                    ? "bg-blue-600 hover:bg-blue-700"
                    : "bg-slate-300 cursor-not-allowed"
                }`}
            >
              Start Reconciliation
            </button>

            <p className="text-center text-slate-400 text-xs mt-4">
              Supported formats: CSV, XLSX, XLS
            </p>
          </div>
        )}

        {/* Loading State */}
        {appState === "loading" && (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="w-10 h-10 border-3 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
            <p className="mt-4 text-slate-600">Processing files...</p>
          </div>
        )}

        {/* Results State */}
        {appState === "results" && results && (
          <div className="space-y-6">
            {/* Success Message */}
            <div className="p-4 bg-green-50 border border-green-200 rounded-md text-green-700 text-sm">
              ✓ Reconciliation completed successfully!
            </div>

            <SummaryCards summary={results.summary} />

            <CategoryTabs
              category5={results.category_5}
              category6={results.category_6}
              category7={results.category_7}
              totals={{
                category_5_total: results.pagination.category_5_total,
                category_6_total: results.pagination.category_6_total,
                category_7_total: results.pagination.category_7_total,
              }}
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 mt-auto">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <p className="text-center text-slate-400 text-sm">
            Financial Reconciliation System • Koshai Assignment
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
