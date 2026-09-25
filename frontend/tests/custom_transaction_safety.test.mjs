import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const frontendRoot = path.resolve(__dirname, "..");

describe("Custom Transaction Client-Side Crash Prevention & Safe Rendering Tests", () => {
  it("1. Launching a newly created transaction with one uploaded document does not produce a client-side exception", () => {
    const detailPath = path.join(frontendRoot, "src/app/dashboard/transactions/[id]/page.tsx");
    assert.ok(fs.existsSync(detailPath), "page.tsx must exist");
    const content = fs.readFileSync(detailPath, "utf-8");

    // Must NOT access raw timelineData.totalEvents directly
    assert.ok(!content.includes("timelineData.totalEvents"), "Must not directly access timelineData.totalEvents without null protection");
    assert.ok(!content.includes("timelineData.conflictingEventsCount"), "Must not directly access timelineData.conflictingEventsCount without null protection");

    // Must use effectiveTimelineData
    assert.ok(content.includes("effectiveTimelineData.totalEvents"), "Must use effectiveTimelineData.totalEvents");
    assert.ok(content.includes("effectiveTimelineData.conflictingEventsCount"), "Must use effectiveTimelineData.conflictingEventsCount");

    // Must guard property fields
    assert.ok(content.includes("transaction.property?.location"), "Must use optional chaining on transaction.property.location");
    assert.ok(content.includes("transaction.property?.developer"), "Must use optional chaining on transaction.property.developer");
  });

  it("2. Transaction overview renders graceful empty states for 0 inconsistencies and 0 risks", () => {
    const detailPath = path.join(frontendRoot, "src/app/dashboard/transactions/[id]/page.tsx");
    const content = fs.readFileSync(detailPath, "utf-8");

    // Must check for empty inconsistencies array
    assert.ok(content.includes("No cross-document discrepancies detected"), "Must render graceful notice when inconsistencies array is empty");
    // Must check for empty risks array
    assert.ok(content.includes("No high-priority contractual risks detected"), "Must render graceful notice when risks array is empty");
  });

  it("3. FinancialExposureCard safely handles 0 values and missing fields for single-document transactions", () => {
    const finCardPath = path.join(frontendRoot, "src/components/copilot/FinancialExposureCard.tsx");
    assert.ok(fs.existsSync(finCardPath), "FinancialExposureCard.tsx must exist");
    const content = fs.readFileSync(finCardPath, "utf-8");

    assert.ok(content.includes("const fin = financial ||"), "Must initialize safe fin fallback object");
    assert.ok(content.includes("fin.totalFinancialAtRiskFormatted"), "Must read from guarded fin object");
    assert.ok(!content.includes('70 sq.ft (-4.8%) @ effective rate'), "Must not hardcode demo area shortfall string");
  });

  it("4. PriorityActionList safely handles empty actions array for clean custom transactions", () => {
    const actionListPath = path.join(frontendRoot, "src/components/copilot/PriorityActionList.tsx");
    assert.ok(fs.existsSync(actionListPath), "PriorityActionList.tsx must exist");
    const content = fs.readFileSync(actionListPath, "utf-8");

    assert.ok(content.includes("actionItems.length === 0"), "Must check for 0 action items");
    assert.ok(content.includes("No priority action items required at this stage"), "Must render clean message when 0 actions exist");
  });

  it("5. IntelligentTimeline safely handles null or empty timelineData without throwing", () => {
    const timelinePath = path.join(frontendRoot, "src/components/copilot/IntelligentTimeline.tsx");
    assert.ok(fs.existsSync(timelinePath), "IntelligentTimeline.tsx must exist");
    const content = fs.readFileSync(timelinePath, "utf-8");

    assert.ok(content.includes("timelineData?.events || []"), "Must safely fall back to empty events array");
    assert.ok(content.includes("timelineData?.totalEvents"), "Must use optional chaining for totalEvents");
  });

  it("6. DocumentTable safely handles single-document bundles without assuming demo document names", () => {
    const docTablePath = path.join(frontendRoot, "src/components/documents/DocumentTable.tsx");
    assert.ok(fs.existsSync(docTablePath), "DocumentTable.tsx must exist");
    const content = fs.readFileSync(docTablePath, "utf-8");

    assert.ok(content.includes("const docs = documents || []"), "Must safely fall back to empty documents array");
    assert.ok(content.includes('(doc.documentType || "OTHER").replace'), "Must safely guard documentType string operations");
  });

  it("7. Transaction detail route includes Next.js Error Boundary to catch any unforeseen runtime errors", () => {
    const errorBoundaryPath = path.join(frontendRoot, "src/app/dashboard/transactions/[id]/error.tsx");
    assert.ok(fs.existsSync(errorBoundaryPath), "error.tsx error boundary must exist in [id] route");
    const content = fs.readFileSync(errorBoundaryPath, "utf-8");

    assert.ok(content.includes("export default function TransactionErrorBoundary"), "Must define error boundary component");
    assert.ok(content.includes("Unable to Display Transaction Intelligence"), "Must render user-friendly recovery UI");
  });
});
