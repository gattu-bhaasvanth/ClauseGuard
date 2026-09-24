import { test, describe } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const frontendRoot = path.resolve(__dirname, "..");

describe("Phase 9 Frontend Intelligence & ML UI Integration Tests", () => {
  test("1. Phase 9 TypeScript types and definitions exist", () => {
    const typesPath = path.join(frontendRoot, "src", "types", "intelligence.ts");
    assert.ok(fs.existsSync(typesPath), "src/types/intelligence.ts must exist");
    const content = fs.readFileSync(typesPath, "utf-8");

    assert.ok(content.includes("export interface EnhancedClause"), "Must define EnhancedClause");
    assert.ok(content.includes("confidence?: number"), "EnhancedClause must have confidence");
    assert.ok(content.includes("classificationSource?:"), "EnhancedClause must have classificationSource");
    assert.ok(content.includes("topAlternatives?:"), "EnhancedClause must have topAlternatives");
    assert.ok(content.includes("export interface EngineStatus"), "Must define EngineStatus");
    assert.ok(content.includes("baseline_macro_f1: number"), "EngineStatus must have baseline_macro_f1");
    assert.ok(content.includes("current_macro_f1: number"), "EngineStatus must have current_macro_f1");
    assert.ok(content.includes("improvement_delta_f1: number"), "EngineStatus must have improvement_delta_f1");
    assert.ok(content.includes("export interface BenchmarkComparison"), "Must define BenchmarkComparison");
    assert.ok(content.includes("promotion_gate_passed: boolean"), "BenchmarkComparison must have promotion_gate_passed");
    assert.ok(content.includes("export interface ClassifyResponse"), "Must define ClassifyResponse");
  });

  test("2. ModelConfidenceBadge component exists with multi-tier confidence styling", () => {
    const badgePath = path.join(
      frontendRoot,
      "src",
      "components",
      "intelligence",
      "ModelConfidenceBadge.tsx"
    );
    assert.ok(fs.existsSync(badgePath), "ModelConfidenceBadge.tsx must exist");
    const content = fs.readFileSync(badgePath, "utf-8");

    assert.ok(content.includes("export function ModelConfidenceBadge"), "Must export ModelConfidenceBadge");
    assert.ok(content.includes("data-testid=\"model-confidence-badge\""), "Must have data-testid for badge");
    assert.ok(content.includes("Review Needed"), "Must show review needed for low confidence (<65%)");
    assert.ok(content.includes("emerald"), "Must have high confidence emerald styling");
    assert.ok(content.includes("amber"), "Must have review amber styling");
    assert.ok(content.includes("ML"), "Must display ML/Rule indicator");
  });

  test("3. ClassificationInspectorDrawer component exists with full explainability layout", () => {
    const drawerPath = path.join(
      frontendRoot,
      "src",
      "components",
      "intelligence",
      "ClassificationInspectorDrawer.tsx"
    );
    assert.ok(fs.existsSync(drawerPath), "ClassificationInspectorDrawer.tsx must exist");
    const content = fs.readFileSync(drawerPath, "utf-8");

    assert.ok(content.includes("export function ClassificationInspectorDrawer"), "Must export ClassificationInspectorDrawer");
    assert.ok(content.includes("data-testid=\"classification-inspector-drawer\""), "Must have data-testid for drawer");
    assert.ok(content.includes("data-testid=\"drawer-close-btn\""), "Must have data-testid for close button");
    assert.ok(content.includes("Escape"), "Must handle Escape key for accessibility");
    assert.ok(content.includes("Primary Classification"), "Must display primary classification section");
    assert.ok(content.includes("Calibrated Confidence"), "Must display calibrated confidence bar");
    assert.ok(content.includes("Top Alternative Categories"), "Must display top alternatives");
    assert.ok(content.includes("Statutory Risk Assessment"), "Must display deterministic statutory risk");
    assert.ok(content.includes("Raw Legal Excerpt"), "Must display verbatim legal excerpt");
    assert.ok(content.includes("Model Version:"), "Must display model version in audit provenance");
    assert.ok(content.includes("Dataset Provenance:"), "Must display dataset provenance");
  });

  test("4. ModelDiagnosticsHub component exists with benchmark cards, bake-off table, and live sandbox", () => {
    const hubPath = path.join(
      frontendRoot,
      "src",
      "components",
      "intelligence",
      "ModelDiagnosticsHub.tsx"
    );
    assert.ok(fs.existsSync(hubPath), "ModelDiagnosticsHub.tsx must exist");
    const content = fs.readFileSync(hubPath, "utf-8");

    assert.ok(content.includes("export function ModelDiagnosticsHub"), "Must export ModelDiagnosticsHub");
    assert.ok(content.includes("data-testid=\"model-diagnostics-hub\""), "Must have data-testid for diagnostics hub");
    assert.ok(content.includes("Baseline Macro F1 (Phase 4)"), "Must show Phase 4 baseline metric");
    assert.ok(content.includes("Current Model Macro F1"), "Must show active model metric");
    assert.ok(content.includes("Improvement Delta (Δ F1)"), "Must show improvement delta");
    assert.ok(content.includes("Architecture Bake-Off Comparison"), "Must show bake-off comparison table");
    assert.ok(content.includes("Candidate C: Semantic Prototype Manifold"), "Must highlight selected Candidate C");
    assert.ok(content.includes("data-testid=\"test-classify-btn\""), "Must have live testing sandbox button");
    assert.ok(content.includes("Live Hybrid Classification Inspector"), "Must display interactive testing section");
  });

  test("5. Settings page integrates ModelDiagnosticsHub in isolated diagnostics section", () => {
    const settingsPath = path.join(
      frontendRoot,
      "src",
      "app",
      "dashboard",
      "settings",
      "page.tsx"
    );
    assert.ok(fs.existsSync(settingsPath), "dashboard/settings/page.tsx must exist");
    const content = fs.readFileSync(settingsPath, "utf-8");

    assert.ok(content.includes("ModelDiagnosticsHub"), "Settings page must import ModelDiagnosticsHub");
    assert.ok(content.includes("<ModelDiagnosticsHub />"), "Settings page must render ModelDiagnosticsHub");
  });

  test("6. Document Analysis Workspace integrates ClauseList with onInspectClause and EvidenceDrawer with onInspectAI", () => {
    const analysisPath = path.join(
      frontendRoot,
      "src",
      "app",
      "dashboard",
      "transactions",
      "[id]",
      "analysis",
      "page.tsx"
    );
    assert.ok(fs.existsSync(analysisPath), "dashboard/transactions/[id]/analysis/page.tsx must exist");
    const content = fs.readFileSync(analysisPath, "utf-8");

    assert.ok(content.includes("ClassificationInspectorDrawer"), "Analysis page must import ClassificationInspectorDrawer");
    assert.ok(content.includes("handleOpenInspector"), "Analysis page must define handleOpenInspector");
    assert.ok(content.includes("onInspectClause={handleOpenInspector}"), "ClauseList must receive onInspectClause");
    assert.ok(content.includes("onInspectAI="), "EvidenceDrawer must receive onInspectAI");
    assert.ok(content.includes("<ClassificationInspectorDrawer"), "Analysis page must render ClassificationInspectorDrawer");
  });

  test("7. ClauseList and EvidenceDrawer render ModelConfidenceBadge", () => {
    const listPath = path.join(frontendRoot, "src", "components", "analysis", "ClauseList.tsx");
    assert.ok(fs.existsSync(listPath), "ClauseList.tsx must exist");
    const listContent = fs.readFileSync(listPath, "utf-8");
    assert.ok(listContent.includes("ModelConfidenceBadge"), "ClauseList must import ModelConfidenceBadge");
    assert.ok(listContent.includes("<ModelConfidenceBadge"), "ClauseList must render ModelConfidenceBadge");

    const drawerPath = path.join(frontendRoot, "src", "components", "analysis", "EvidenceDrawer.tsx");
    assert.ok(fs.existsSync(drawerPath), "EvidenceDrawer.tsx must exist");
    const drawerContent = fs.readFileSync(drawerPath, "utf-8");
    assert.ok(drawerContent.includes("ModelConfidenceBadge"), "EvidenceDrawer must import ModelConfidenceBadge");
    assert.ok(drawerContent.includes("<ModelConfidenceBadge"), "EvidenceDrawer must render ModelConfidenceBadge");
    assert.ok(drawerContent.includes("Inspect AI Classification & Alternatives"), "EvidenceDrawer must render action button");
  });

  test("8. API client implements Phase 9 endpoints with safe offline fallbacks", () => {
    const apiPath = path.join(frontendRoot, "src", "lib", "api.ts");
    assert.ok(fs.existsSync(apiPath), "src/lib/api.ts must exist");
    const content = fs.readFileSync(apiPath, "utf-8");

    assert.ok(content.includes("fetchEngineStatus"), "API client must export fetchEngineStatus");
    assert.ok(content.includes("/intelligence/engine-status"), "Must call engine-status endpoint");
    assert.ok(content.includes("fetchBenchmarks"), "API client must export fetchBenchmarks");
    assert.ok(content.includes("/intelligence/benchmarks"), "Must call benchmarks endpoint");
    assert.ok(content.includes("classifyClausePreview"), "API client must export classifyClausePreview");
    assert.ok(content.includes("/intelligence/classify"), "Must call classify endpoint");
  });
});
