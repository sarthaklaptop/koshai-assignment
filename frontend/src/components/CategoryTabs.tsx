import { useState } from "react";

interface CategoryTabsProps {
  category5: Record<string, unknown>[];
  category6: Record<string, unknown>[];
  category7: Record<string, unknown>[];
  totals: {
    category_5_total: number;
    category_6_total: number;
    category_7_total: number;
  };
}

type TabKey = "cat5" | "cat6" | "cat7";

export function CategoryTabs({
  category5,
  category6,
  category7,
  totals,
}: CategoryTabsProps) {
  const [activeTab, setActiveTab] = useState<TabKey>("cat5");

  // get data for current tab
  let data: Record<string, unknown>[] = [];
  let count = 0;

  if (activeTab === "cat5") {
    data = category5;
    count = totals.category_5_total;
  } else if (activeTab === "cat6") {
    data = category6;
    count = totals.category_6_total;
  } else {
    data = category7;
    count = totals.category_7_total;
  }

  // get columns from first row, filter out internal columns
  const columns = data.length > 0 ? Object.keys(data[0]) : [];
  const displayColumns = columns.filter(
    (col) => !["_merge", "Category"].includes(col),
  );

  // format cell values for display
  const formatValue = (value: unknown, column: string): string => {
    if (value === null || value === undefined) return "—";

    // format variance columns
    if (column === "Variance" || column === "Variance_Percent") {
      const num = Number(value);
      return num.toFixed(2);
    }

    // format amount columns with dollar sign
    if (
      column.toLowerCase().includes("amount") ||
      column.toLowerCase().includes("amt")
    ) {
      const num = Number(value);
      if (!isNaN(num)) {
        return `$${num.toFixed(2)}`;
      }
    }

    return String(value);
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
      {/* Tab buttons */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab("cat5")}
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === "cat5"
              ? "text-green-600 bg-green-50 border-b-2 border-green-500"
              : "text-slate-500 hover:bg-slate-50"
          }`}
        >
          Matched ({totals.category_5_total})
        </button>
        <button
          onClick={() => setActiveTab("cat6")}
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === "cat6"
              ? "text-amber-600 bg-amber-50 border-b-2 border-amber-500"
              : "text-slate-500 hover:bg-slate-50"
          }`}
        >
          Settlement Only ({totals.category_6_total})
        </button>
        <button
          onClick={() => setActiveTab("cat7")}
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === "cat7"
              ? "text-red-600 bg-red-50 border-b-2 border-red-500"
              : "text-slate-500 hover:bg-slate-50"
          }`}
        >
          Statement Only ({totals.category_7_total})
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto max-h-96 overflow-y-auto">
        {data.length > 0 ? (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 sticky top-0">
              <tr>
                {displayColumns.map((col) => (
                  <th
                    key={col}
                    className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide"
                  >
                    {col.replace(/_/g, " ")}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-50">
                  {displayColumns.map((col) => (
                    <td
                      key={col}
                      className="px-4 py-3 text-slate-600 whitespace-nowrap"
                    >
                      {formatValue(row[col], col)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="py-12 text-center text-slate-400">
            No records in this category
          </div>
        )}
      </div>

      {/* Footer */}
      {data.length > 0 && (
        <div className="px-4 py-2 border-t border-slate-200 bg-slate-50 text-xs text-slate-500">
          Showing {data.length} of {count} records
        </div>
      )}
    </div>
  );
}
