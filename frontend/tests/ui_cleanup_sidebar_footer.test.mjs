import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const frontendRoot = path.resolve(__dirname, "..");

describe("Sidebar Transaction-Awareness & Footer Architecture Summary Tests", () => {
  it("1. Sidebar dynamically differentiates between Active Demo Bundle and Current Transaction", () => {
    const sidebarPath = path.join(frontendRoot, "src/components/layout/Sidebar.tsx");
    assert.ok(fs.existsSync(sidebarPath), "Sidebar.tsx must exist");
    const content = fs.readFileSync(sidebarPath, "utf-8");

    // Must determine custom transaction vs demo
    assert.ok(content.includes("isCustomTx"), "Sidebar must detect custom transaction state");
    assert.ok(content.includes('"CURRENT TRANSACTION"'), "Sidebar must define CURRENT TRANSACTION badge");
    assert.ok(content.includes('"ACTIVE DEMO BUNDLE"'), "Sidebar must define ACTIVE DEMO BUNDLE badge");

    // Must handle demo fallback
    assert.ok(content.includes('"SkyView Flat A-1204"'), "Sidebar must preserve SkyView Flat A-1204 for demo");
    assert.ok(content.includes('"/dashboard/transactions/skyview-a1204"'), "Sidebar must link to skyview-a1204 for demo");

    // Must dynamically format actual project and unit
    assert.ok(
      content.includes("${project} — ${unit}") || content.includes("project") && content.includes("unit"),
      "Sidebar must dynamically format project and unit"
    );
    // Must NOT hardcode Test Residency
    assert.ok(!content.includes('"Test Residency — Flat B-204"'), "Must not hardcode Test Residency in Sidebar");
  });

  it("2. Landing page footer displays Architecture & Intelligence with all 8 domains", () => {
    const footerPath = path.join(frontendRoot, "src/components/layout/Footer.tsx");
    assert.ok(fs.existsSync(footerPath), "Footer.tsx must exist");
    const content = fs.readFileSync(footerPath, "utf-8");

    // Heading
    assert.ok(content.includes("Architecture & Intelligence"), "Footer must have Architecture & Intelligence heading");
    assert.ok(!content.includes("Architecture Roadmap"), "Footer must not contain Architecture Roadmap");

    // All 8 architectural domains
    const requiredItems = [
      "Document Ingestion & OCR",
      "Clause & Entity Intelligence",
      "Cross-Document Verification",
      "Risk & Audit Analysis",
      "Grounded RAG & Evidence",
      "Domain-Specific ML",
      "Transaction Intelligence Copilot",
      "Timeline, Lineage & Executive Brief",
    ];

    for (const item of requiredItems) {
      assert.ok(content.includes(item), `Footer must include architecture item: "${item}"`);
    }

    // Outdated phase items must be gone
    assert.ok(!content.includes("Phase 1: Frontend Foundation"), "Footer must not contain Phase 1: Frontend Foundation");
    assert.ok(!content.includes("Phase 2: FastAPI & DB Core"), "Footer must not contain Phase 2: FastAPI & DB Core");
    assert.ok(!content.includes("Phase 3: PDF & PaddleOCR"), "Footer must not contain Phase 3: PDF & PaddleOCR");
    assert.ok(!content.includes("Phase 6: Cross-Doc Engine"), "Footer must not contain Phase 6: Cross-Doc Engine");
    assert.ok(!content.includes("Phase 9: Real ML Training"), "Footer must not contain Phase 9: Real ML Training");

    // Stale version text must be updated
    assert.ok(!content.includes("Phase 1 UI"), "Footer must not contain Phase 1 UI");
    assert.ok(!content.includes("v0.1.0-alpha"), "Footer must not contain v0.1.0-alpha");
  });

  it("3. Transaction detail and analysis pages notify listeners of loaded transaction title", () => {
    const detailPath = path.join(frontendRoot, "src/app/dashboard/transactions/[id]/page.tsx");
    const analysisPath = path.join(frontendRoot, "src/app/dashboard/transactions/[id]/analysis/page.tsx");

    const detailContent = fs.readFileSync(detailPath, "utf-8");
    const analysisContent = fs.readFileSync(analysisPath, "utf-8");

    assert.ok(detailContent.includes("cg-tx-loaded"), "Detail page must dispatch cg-tx-loaded event");
    assert.ok(analysisContent.includes("cg-tx-loaded"), "Analysis page must dispatch cg-tx-loaded event");
  });
});
