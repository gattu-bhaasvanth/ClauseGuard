import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const frontendRoot = path.resolve(__dirname, "..");

describe("New Transaction Demo-Data Isolation Regression Tests", () => {
  it("1. DocumentDropzone does not preload SkyView demo documents by default", () => {
    const dropzonePath = path.join(frontendRoot, "src/components/documents/DocumentDropzone.tsx");
    assert.ok(fs.existsSync(dropzonePath), "DocumentDropzone.tsx must exist");
    const content = fs.readFileSync(dropzonePath, "utf-8");

    // Must default initialFiles to empty array []
    assert.ok(content.includes("initialFiles = []"), "initialFiles must default to empty array");
    // State must initialize with initialFiles
    assert.ok(content.includes("useState<SelectedFileItem[]>(initialFiles)"), "selectedFiles state must initialize with initialFiles");
  });

  it("2. New transaction page starts with empty/unpreloaded property form data", () => {
    const newTxPagePath = path.join(frontendRoot, "src/app/dashboard/transactions/new/page.tsx");
    assert.ok(fs.existsSync(newTxPagePath), "new/page.tsx must exist");
    const content = fs.readFileSync(newTxPagePath, "utf-8");

    // Verify initial form state is empty, not SkyView
    assert.ok(!content.includes('projectName: "SkyView Residency"'), "Form must not preload SkyView Residency");
    assert.ok(!content.includes('unit: "Flat A-1204"'), "Form must not preload Flat A-1204");
    assert.ok(!content.includes('developer: "Skyline Infra Developers Ltd."'), "Form must not preload Skyline Infra");
  });

  it("3. Step 3 renders dynamic document count and actual document types, not demo strings", () => {
    const newTxPagePath = path.join(frontendRoot, "src/app/dashboard/transactions/new/page.tsx");
    const content = fs.readFileSync(newTxPagePath, "utf-8");

    // Must NOT contain hardcoded "3 Documents Configured"
    assert.ok(!content.includes('"3 Documents Configured"'), 'Step 3 must not hardcode "3 Documents Configured"');
    // Must NOT contain hardcoded "BBA, Allotment Letter, Brochure"
    assert.ok(!content.includes('"BBA, Allotment Letter, Brochure"'), 'Step 3 must not hardcode "BBA, Allotment Letter, Brochure"');

    // Must dynamically format count from files
    assert.ok(content.includes("files.length"), "Step 3 must compute document count from files.length");
    assert.ok(content.includes("DOCUMENT_TYPE_LABELS"), "Step 3 must look up document types dynamically");
  });

  it("4. New transaction launch calls API dynamically and redirects to created ID, not demo ID", () => {
    const newTxPagePath = path.join(frontendRoot, "src/app/dashboard/transactions/new/page.tsx");
    const content = fs.readFileSync(newTxPagePath, "utf-8");

    // Must call createTransaction
    assert.ok(content.includes("createTransaction("), "Must call createTransaction API function");
    // Must NOT unconditionally push /dashboard/transactions/skyview-a1204
    assert.ok(!content.includes('router.push("/dashboard/transactions/skyview-a1204")'), "Must navigate to created transaction ID rather than hardcoded skyview-a1204");
  });

  it("5. API client does not fall back to MOCK_SKYVIEW_TRANSACTION for custom transaction IDs", () => {
    const apiPath = path.join(frontendRoot, "src/lib/api.ts");
    assert.ok(fs.existsSync(apiPath), "api.ts must exist");
    const content = fs.readFileSync(apiPath, "utf-8");

    // Must provide createTransaction and uploadTransactionDocument
    assert.ok(content.includes("export async function createTransaction"), "api.ts must export createTransaction");
    assert.ok(content.includes("export async function uploadTransactionDocument"), "api.ts must export uploadTransactionDocument");

    // fetchTransactionById must only fallback to MOCK_SKYVIEW_TRANSACTION if id === "skyview-a1204"
    assert.ok(content.includes('if (id === "skyview-a1204") return MOCK_SKYVIEW_TRANSACTION;'), "fetchTransactionById must isolate demo mock fallback to skyview-a1204 only");
  });

  it("6. Transaction dashboard dynamically loads transaction by ID instead of hardcoding demo transaction", () => {
    const detailPath = path.join(frontendRoot, "src/app/dashboard/transactions/[id]/page.tsx");
    assert.ok(fs.existsSync(detailPath), "transactions/[id]/page.tsx must exist");
    const content = fs.readFileSync(detailPath, "utf-8");

    // Must NOT have static assignment: const transaction = MOCK_SKYVIEW_TRANSACTION;
    assert.ok(!content.includes("const transaction = MOCK_SKYVIEW_TRANSACTION;"), "Must not assign static MOCK_SKYVIEW_TRANSACTION");
    assert.ok(content.includes("fetchTransactionById("), "Must fetch transaction dynamically via fetchTransactionById");
  });
});
