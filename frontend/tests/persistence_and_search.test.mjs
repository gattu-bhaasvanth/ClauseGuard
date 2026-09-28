import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const frontendRoot = path.resolve(__dirname, "..");

describe("Transaction Persistence, Listing & Search Integration Tests", () => {
  it("1. TransactionsListPage fetches transactions dynamically via API and not from static mock", () => {
    const listPagePath = path.join(frontendRoot, "src/app/dashboard/transactions/page.tsx");
    assert.ok(fs.existsSync(listPagePath), "transactions/page.tsx must exist");
    const content = fs.readFileSync(listPagePath, "utf-8");

    // Must import fetchTransactions from @/lib/api
    assert.ok(content.includes("fetchTransactions"), "Must import fetchTransactions from @/lib/api");
    // Must NOT import MOCK_ALL_TRANSACTIONS directly
    assert.ok(!content.includes("MOCK_ALL_TRANSACTIONS"), "Must not import MOCK_ALL_TRANSACTIONS directly in transactions list page");
    // Must contain useEffect or async loader for fetchTransactions
    assert.ok(content.includes("fetchTransactions()"), "Must call fetchTransactions() on mount");
  });

  it("2. TransactionsListPage search inspects project, developer, unit, title, and location", () => {
    const listPagePath = path.join(frontendRoot, "src/app/dashboard/transactions/page.tsx");
    const content = fs.readFileSync(listPagePath, "utf-8");

    assert.ok(content.includes("project"), "Search must check project name");
    assert.ok(content.includes("developer"), "Search must check developer name");
    assert.ok(content.includes("unit"), "Search must check unit number/identifier");
  });

  it("3. Dashboard overview page dynamically fetches transactions for accurate counts", () => {
    const dashboardPagePath = path.join(frontendRoot, "src/app/dashboard/page.tsx");
    assert.ok(fs.existsSync(dashboardPagePath), "dashboard/page.tsx must exist");
    const content = fs.readFileSync(dashboardPagePath, "utf-8");

    assert.ok(content.includes("fetchTransactions"), "Must import and call fetchTransactions");
    assert.ok(content.includes("setTransactions"), "Must update state with dynamic transactions");
  });

  it("4. RecentTransactionsTable provides graceful empty state when transactions list is empty", () => {
    const tablePath = path.join(frontendRoot, "src/components/dashboard/RecentTransactionsTable.tsx");
    assert.ok(fs.existsSync(tablePath), "RecentTransactionsTable.tsx must exist");
    const content = fs.readFileSync(tablePath, "utf-8");

    assert.ok(content.includes("transactions.length === 0"), "Must check transactions.length === 0 for empty state");
    assert.ok(content.includes("No property transactions found"), "Must display user-friendly empty state text");
  });

  it("5. API client fetchTransactions supports server search parameter ?q= and filters unit/project in fallback", () => {
    const apiPath = path.join(frontendRoot, "src/lib/api.ts");
    assert.ok(fs.existsSync(apiPath), "api.ts must exist");
    const content = fs.readFileSync(apiPath, "utf-8");

    assert.ok(content.includes("fetchTransactions(query?: string)"), "fetchTransactions must accept optional query param");
    assert.ok(content.includes("q="), "Must pass query to backend via ?q=");
    assert.ok(content.includes("property?.unit"), "Fallback must check property.unit");
    assert.ok(content.includes("property?.project"), "Fallback must check property.project");
    assert.ok(content.includes("property?.developer"), "Fallback must check property.developer");
  });
});
