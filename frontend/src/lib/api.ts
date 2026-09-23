import { Transaction } from "@/types/transaction";
import {
  MOCK_ALL_TRANSACTIONS,
  MOCK_SKYVIEW_TRANSACTION,
} from "@/mock/demoData";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/**
 * Fetch all transaction bundles from FastAPI backend,
 * falling back to local mock data if the backend is not reachable.
 */
export async function fetchTransactions(): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE}/transactions`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    return MOCK_ALL_TRANSACTIONS;
  }
}

/**
 * Fetch a single transaction bundle by ID from FastAPI backend,
 * falling back to the corresponding mock bundle if the backend is unreachable.
 */
export async function fetchTransactionById(id: string): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/transactions/${id}`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    if (id === "skyview-a1204") return MOCK_SKYVIEW_TRANSACTION;
    const found = MOCK_ALL_TRANSACTIONS.find((t) => t.id === id);
    return found || MOCK_SKYVIEW_TRANSACTION;
  }
}

/**
 * Check backend health status.
 */
export async function checkBackendHealth(): Promise<{
  online: boolean;
  data?: any;
}> {
  try {
    const res = await fetch(`${API_BASE}/health`, {
      cache: "no-store",
    });
    if (!res.ok) return { online: false };
    const data = await res.json();
    return { online: true, data };
  } catch {
    return { online: false };
  }
}
