import type { ReconciliationSummary } from "../api";

interface SummaryCardsProps {
  summary: ReconciliationSummary;
}

export function SummaryCards({ summary }: SummaryCardsProps) {
  return (
    <div className="space-y-4">
      {/* Main category cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg p-4 border border-slate-200 shadow-sm">
          <p className="text-slate-500 text-sm">Category 5</p>
          <p className="text-xs text-slate-400">Matched (Both Files)</p>
          <p className="text-2xl font-semibold text-green-600 mt-2">
            {summary.category_5_count}
          </p>
        </div>

        <div className="bg-white rounded-lg p-4 border border-slate-200 shadow-sm">
          <p className="text-slate-500 text-sm">Category 6</p>
          <p className="text-xs text-slate-400">Settlement Only</p>
          <p className="text-2xl font-semibold text-amber-500 mt-2">
            {summary.category_6_count}
          </p>
        </div>

        <div className="bg-white rounded-lg p-4 border border-slate-200 shadow-sm">
          <p className="text-slate-500 text-sm">Category 7</p>
          <p className="text-xs text-slate-400">Statement Only</p>
          <p className="text-2xl font-semibold text-red-500 mt-2">
            {summary.category_7_count}
          </p>
        </div>

        <div className="bg-white rounded-lg p-4 border border-slate-200 shadow-sm">
          <p className="text-slate-500 text-sm">Total Variance</p>
          <p className="text-xs text-slate-400">Settlement - Statement</p>
          <p
            className={`text-2xl font-semibold mt-2 ${summary.total_variance >= 0 ? "text-blue-600" : "text-red-500"}`}
          >
            $
            {summary.total_variance.toLocaleString(undefined, {
              minimumFractionDigits: 2,
            })}
          </p>
        </div>
      </div>

      {/* Additional stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-slate-100 rounded-md p-3 text-center">
          <p className="text-slate-500 text-xs">Statement Records</p>
          <p className="text-lg font-medium text-slate-700">
            {summary.total_statement_records}
          </p>
        </div>
        <div className="bg-slate-100 rounded-md p-3 text-center">
          <p className="text-slate-500 text-xs">Settlement Records</p>
          <p className="text-lg font-medium text-slate-700">
            {summary.total_settlement_records}
          </p>
        </div>
        <div className="bg-slate-100 rounded-md p-3 text-center">
          <p className="text-slate-500 text-xs">Avg Variance</p>
          <p className="text-lg font-medium text-slate-700">
            ${summary.avg_variance.toFixed(2)}
          </p>
        </div>
        <div className="bg-slate-100 rounded-md p-3 text-center">
          <p className="text-slate-500 text-xs">Variance Range</p>
          <p className="text-lg font-medium text-slate-700">
            ${summary.min_variance.toFixed(2)} → $
            {summary.max_variance.toFixed(2)}
          </p>
        </div>
      </div>
    </div>
  );
}
