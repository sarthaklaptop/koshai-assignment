import axios from "axios";

// Use env variable in production, localhost in dev
const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export interface ReconciliationSummary {
  total_statement_records: number;
  total_settlement_records: number;
  reconcilable_statement: number;
  reconcilable_settlement: number;
  category_5_count: number;
  category_6_count: number;
  category_7_count: number;
  total_variance: number;
  avg_variance: number;
  max_variance: number;
  min_variance: number;
}

export interface ReconciliationResponse {
  success: boolean;
  message: string;
  summary: ReconciliationSummary;
  category_5: Record<string, unknown>[];
  category_6: Record<string, unknown>[];
  category_7: Record<string, unknown>[];
  pagination: {
    limit: number;
    category_5_total: number;
    category_6_total: number;
    category_7_total: number;
  };
}

export const reconcileFiles = async (
  statementFile: File,
  settlementFile: File,
): Promise<ReconciliationResponse> => {
  const formData = new FormData();
  formData.append("statement_file", statementFile);
  formData.append("settlement_file", settlementFile);

  // Pass correct column names for Settlement file
  const params = new URLSearchParams({
    settlement_pin_col: "PartnerPin",
    settlement_type_col: "Status",
    settlement_rate_col: "APIRATE",
  });

  const response = await axios.post<ReconciliationResponse>(
    `${API_BASE_URL}/reconcile?${params.toString()}`,
    formData,
  );
  return response.data;
};

export const checkHealth = async (): Promise<{ status: string }> => {
  const response = await axios.get(`${API_BASE_URL}/health`);
  return response.data;
};
