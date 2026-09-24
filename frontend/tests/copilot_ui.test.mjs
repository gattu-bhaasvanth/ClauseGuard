import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const frontendRoot = path.resolve(__dirname, "..");

describe("Phase 10 Frontend Intelligence & Copilot UI Integration Tests", () => {
  it("1. Phase 10 TypeScript types and definitions exist", () => {
    const typesPath = path.join(frontendRoot, "src/types/copilot.ts");
    assert.ok(fs.existsSync(typesPath), "copilot.ts should exist");
    const content = fs.readFileSync(typesPath, "utf-8");
    assert.ok(content.includes("export interface RiskVectorItem"), "Should define RiskVectorItem");
    assert.ok(content.includes("export interface FinancialExposureBreakdown"), "Should define FinancialExposureBreakdown");
    assert.ok(content.includes("export interface PriorityActionItem"), "Should define PriorityActionItem");
    assert.ok(content.includes("export interface TransactionCommandCenterData"), "Should define TransactionCommandCenterData");
    assert.ok(content.includes("export interface CopilotCitation"), "Should define CopilotCitation");
    assert.ok(content.includes("export interface CopilotQueryResponse"), "Should define CopilotQueryResponse");
    assert.ok(content.includes("export interface ExplainableRiskData"), "Should define ExplainableRiskData");
    assert.ok(content.includes("export interface TimelineEvent"), "Should define TimelineEvent");
    assert.ok(content.includes("export interface TransactionBriefData"), "Should define TransactionBriefData");
  });

  it("2. Command Center components exist and render risk vectors & financial exposure", () => {
    const cmdCenterPath = path.join(frontendRoot, "src/components/copilot/TransactionCommandCenter.tsx");
    assert.ok(fs.existsSync(cmdCenterPath), "TransactionCommandCenter.tsx should exist");
    const cmdContent = fs.readFileSync(cmdCenterPath, "utf-8");
    assert.ok(cmdContent.includes("RiskVectorGrid"), "Should render RiskVectorGrid");
    assert.ok(cmdContent.includes("FinancialExposureCard"), "Should render FinancialExposureCard");
    assert.ok(cmdContent.includes("PriorityActionList"), "Should render PriorityActionList");

    const riskGridPath = path.join(frontendRoot, "src/components/copilot/RiskVectorGrid.tsx");
    assert.ok(fs.existsSync(riskGridPath), "RiskVectorGrid.tsx should exist");
    const gridContent = fs.readFileSync(riskGridPath, "utf-8");
    assert.ok(gridContent.includes("financial_exposure"), "Should support financial_exposure vector");
    assert.ok(gridContent.includes("contractual_asymmetry"), "Should support contractual_asymmetry vector");

    const finCardPath = path.join(frontendRoot, "src/components/copilot/FinancialExposureCard.tsx");
    assert.ok(fs.existsSync(finCardPath), "FinancialExposureCard.tsx should exist");
    const finContent = fs.readFileSync(finCardPath, "utf-8");
    assert.ok(finContent.includes("totalFinancialAtRiskFormatted"), "Should display total capital at risk");
    assert.ok(finContent.includes("earnestMoneyForfeitRiskFormatted"), "Should display earnest money forfeiture risk");
  });

  it("3. Copilot components exist with suggestion prompts, chat thread, and citations", () => {
    const panelPath = path.join(frontendRoot, "src/components/copilot/TransactionCopilotPanel.tsx");
    assert.ok(fs.existsSync(panelPath), "TransactionCopilotPanel.tsx should exist");
    const panelContent = fs.readFileSync(panelPath, "utf-8");
    assert.ok(panelContent.includes("role=\"dialog\""), "Should have dialog accessibility role");
    assert.ok(panelContent.includes("queryCopilot"), "Should call queryCopilot API");
    assert.ok(panelContent.includes("Escape"), "Should handle Escape key to close");

    const msgListPath = path.join(frontendRoot, "src/components/copilot/CopilotMessageList.tsx");
    assert.ok(fs.existsSync(msgListPath), "CopilotMessageList.tsx should exist");
    const msgContent = fs.readFileSync(msgListPath, "utf-8");
    assert.ok(msgContent.includes("Grounded in Evidence"), "Should render grounded status");
    assert.ok(msgContent.includes("Evidence Refusal"), "Should render refusal status");
    assert.ok(msgContent.includes("citations"), "Should render citation chips");

    const promptBarPath = path.join(frontendRoot, "src/components/copilot/SuggestedPromptBar.tsx");
    assert.ok(fs.existsSync(promptBarPath), "SuggestedPromptBar.tsx should exist");
  });

  it("4. Explainable Risk Intelligence components exist with 5-tier lineage and statutory benchmarks", () => {
    const drawerPath = path.join(frontendRoot, "src/components/copilot/ExplainableRiskDrawer.tsx");
    assert.ok(fs.existsSync(drawerPath), "ExplainableRiskDrawer.tsx should exist");
    const drawerContent = fs.readFileSync(drawerPath, "utf-8");
    assert.ok(drawerContent.includes("fetchExplainableRisk"), "Should fetch explainable risk data");
    assert.ok(drawerContent.includes("plainEnglishHarm"), "Should render plain English harm");
    assert.ok(drawerContent.includes("statutoryBenchmark"), "Should render statutory benchmark");
    assert.ok(drawerContent.includes("lineage"), "Should render 5-tier lineage");
    assert.ok(drawerContent.includes("Escape"), "Should close on Escape key");

    const quantPath = path.join(frontendRoot, "src/components/copilot/QuantifiedImpactCard.tsx");
    assert.ok(fs.existsSync(quantPath), "QuantifiedImpactCard.tsx should exist");

    const scriptPath = path.join(frontendRoot, "src/components/copilot/NegotiationScriptBox.tsx");
    assert.ok(fs.existsSync(scriptPath), "NegotiationScriptBox.tsx should exist");
    const scriptContent = fs.readFileSync(scriptPath, "utf-8");
    assert.ok(scriptContent.includes("clipboard.writeText"), "Should provide copy functionality");
  });

  it("5. Timeline and Evidence Lineage components exist with 5 certainty states", () => {
    const timelinePath = path.join(frontendRoot, "src/components/copilot/IntelligentTimeline.tsx");
    assert.ok(fs.existsSync(timelinePath), "IntelligentTimeline.tsx should exist");
    const timeContent = fs.readFileSync(timelinePath, "utf-8");
    assert.ok(timeContent.includes("CONTRACTUAL"), "Should support CONTRACTUAL filter");
    assert.ok(timeContent.includes("CONFLICTS"), "Should support CONFLICTS filter");

    const milestoneCardPath = path.join(frontendRoot, "src/components/copilot/MilestoneCard.tsx");
    assert.ok(fs.existsSync(milestoneCardPath), "MilestoneCard.tsx should exist");
    const cardContent = fs.readFileSync(milestoneCardPath, "utf-8");
    assert.ok(cardContent.includes("CONTRACTUAL"), "Should style CONTRACTUAL dates");
    assert.ok(cardContent.includes("INFERRED"), "Should style INFERRED dates");
    assert.ok(cardContent.includes("MARKETING"), "Should style MARKETING dates");
    assert.ok(cardContent.includes("UNCERTAIN"), "Should style UNCERTAIN dates");

    const graphPath = path.join(frontendRoot, "src/components/copilot/EvidenceLineageGraph.tsx");
    assert.ok(fs.existsSync(graphPath), "EvidenceLineageGraph.tsx should exist");
    const graphContent = fs.readFileSync(graphPath, "utf-8");
    assert.ok(graphContent.includes("TRANSACTION"), "Should map TRANSACTION level");
    assert.ok(graphContent.includes("DOCUMENT"), "Should map DOCUMENT level");
    assert.ok(graphContent.includes("PAGE"), "Should map PAGE level");
    assert.ok(graphContent.includes("CLAUSE"), "Should map CLAUSE level");
    assert.ok(graphContent.includes("FINDING"), "Should map FINDING level");
    assert.ok(graphContent.includes("EVIDENCE"), "Should map EVIDENCE level");
  });

  it("6. Executive Transaction Brief components exist with 7 sections and PDF export", () => {
    const briefModalPath = path.join(frontendRoot, "src/components/copilot/TransactionBriefModal.tsx");
    assert.ok(fs.existsSync(briefModalPath), "TransactionBriefModal.tsx should exist");
    const modalContent = fs.readFileSync(briefModalPath, "utf-8");
    assert.ok(modalContent.includes("downloadTransactionBriefPdf"), "Should call PDF download");
    assert.ok(modalContent.includes("fetchTransactionBrief"), "Should fetch brief payload");

    const sectionPreviewPath = path.join(frontendRoot, "src/components/copilot/BriefSectionPreview.tsx");
    assert.ok(fs.existsSync(sectionPreviewPath), "BriefSectionPreview.tsx should exist");
  });

  it("7. Transaction overview page integrates Phase 10 Command Center and Cmd+K keybinding", () => {
    const overviewPagePath = path.join(frontendRoot, "src/app/dashboard/transactions/[id]/page.tsx");
    assert.ok(fs.existsSync(overviewPagePath), "Overview page should exist");
    const pageContent = fs.readFileSync(overviewPagePath, "utf-8");
    assert.ok(pageContent.includes("TransactionCommandCenter"), "Should import and render TransactionCommandCenter");
    assert.ok(pageContent.includes("TransactionCopilotPanel"), "Should import and render TransactionCopilotPanel");
    assert.ok(pageContent.includes("ExplainableRiskDrawer"), "Should import and render ExplainableRiskDrawer");
    assert.ok(pageContent.includes("IntelligentTimeline"), "Should import and render IntelligentTimeline");
    assert.ok(pageContent.includes("EvidenceLineageGraph"), "Should import and render EvidenceLineageGraph");
    assert.ok(pageContent.includes("TransactionBriefModal"), "Should import and render TransactionBriefModal");
    assert.ok(pageContent.includes("metaKey || e.ctrlKey") && pageContent.includes("k"), "Should listen to Cmd+K shortcut");
    assert.ok(pageContent.includes("data-testid=\"header-ask-copilot-btn\""), "Should have header Ask Copilot button");
  });

  it("8. API client implements Phase 10 endpoints with safe offline fallbacks", () => {
    const apiPath = path.join(frontendRoot, "src/lib/api.ts");
    assert.ok(fs.existsSync(apiPath), "api.ts should exist");
    const apiContent = fs.readFileSync(apiPath, "utf-8");
    assert.ok(apiContent.includes("export async function fetchCommandCenter"), "Should export fetchCommandCenter");
    assert.ok(apiContent.includes("export async function queryCopilot"), "Should export queryCopilot");
    assert.ok(apiContent.includes("export async function fetchExplainableRisk"), "Should export fetchExplainableRisk");
    assert.ok(apiContent.includes("export async function fetchTimeline"), "Should export fetchTimeline");
    assert.ok(apiContent.includes("export async function fetchTransactionBrief"), "Should export fetchTransactionBrief");
    assert.ok(apiContent.includes("export async function downloadTransactionBriefPdf"), "Should export downloadTransactionBriefPdf");
  });
});
