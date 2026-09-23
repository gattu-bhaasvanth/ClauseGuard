import { test, describe } from "node:test";
import assert from "node:assert";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const frontendRoot = path.resolve(__dirname, "..");

describe("Phase 8 Frontend RAG UI Integration Tests", () => {
  test("1. RAG TypeScript types and definitions exist", () => {
    const typesPath = path.join(frontendRoot, "src", "types", "rag.ts");
    assert.ok(fs.existsSync(typesPath), "src/types/rag.ts must exist");
    const content = fs.readFileSync(typesPath, "utf-8");

    assert.ok(content.includes("export interface RAGCitation"), "Must define RAGCitation");
    assert.ok(content.includes("documentId: string"), "RAGCitation must have documentId");
    assert.ok(content.includes("pageNumber: number"), "RAGCitation must have pageNumber");
    assert.ok(content.includes("clauseNumber?"), "RAGCitation must have clauseNumber");
    assert.ok(content.includes("relevanceScore: number"), "RAGCitation must have relevanceScore");
    assert.ok(content.includes("export interface RAGQueryResponse"), "Must define RAGQueryResponse");
    assert.ok(content.includes("citations: RAGCitation[]"), "RAGQueryResponse must contain citations");
    assert.ok(content.includes("grounded: boolean"), "RAGQueryResponse must contain grounded flag");
    assert.ok(content.includes("status: \"GROUNDED\" | \"INSUFFICIENT_EVIDENCE\""), "RAGQueryResponse must have status union");
  });

  test("2. SemanticExplorationWorkspace and SourceEvidenceModal components exist with modal support", () => {
    const workspacePath = path.join(
      frontendRoot,
      "src",
      "components",
      "transactions",
      "SemanticExplorationWorkspace.tsx"
    );
    assert.ok(fs.existsSync(workspacePath), "SemanticExplorationWorkspace.tsx must exist");
    const workspaceContent = fs.readFileSync(workspacePath, "utf-8");

    assert.ok(
      workspaceContent.includes("export function SemanticExplorationWorkspace"),
      "Must export SemanticExplorationWorkspace"
    );
    assert.ok(
      workspaceContent.includes("isModal"),
      "Must support isModal prop for popup overlay"
    );
    assert.ok(
      workspaceContent.includes("autoFocusInput"),
      "Must support autoFocusInput prop for search field"
    );
    assert.ok(
      workspaceContent.includes("data-testid=\"rag-query-input\""),
      "Must include data-testid for query input"
    );
    assert.ok(
      workspaceContent.includes("data-testid=\"rag-submit-btn\""),
      "Must include data-testid for submit button"
    );
    assert.ok(
      workspaceContent.includes("id=\"ask-clauseguard-workspace\""),
      "Must define workspace DOM id for scroll targeting"
    );
    assert.ok(
      workspaceContent.includes("Ask ClauseGuard"),
      "Must include Ask ClauseGuard branding"
    );
    assert.ok(
      workspaceContent.includes("SourceEvidenceModal"),
      "Must integrate SourceEvidenceModal"
    );
    assert.ok(
      workspaceContent.includes("SUGGESTED_QUERIES"),
      "Must include suggested prompt chips"
    );

    const modalPath = path.join(
      frontendRoot,
      "src",
      "components",
      "transactions",
      "SourceEvidenceModal.tsx"
    );
    assert.ok(fs.existsSync(modalPath), "SourceEvidenceModal.tsx must exist");
    const modalContent = fs.readFileSync(modalPath, "utf-8");

    assert.ok(
      modalContent.includes("export function SourceEvidenceModal"),
      "Must export SourceEvidenceModal"
    );
    assert.ok(
      modalContent.includes("Verbatim Contractual Excerpt"),
      "Must display verbatim excerpt"
    );
  });

  test("3. Header Ask ClauseGuard button triggers active click handler and opens modal overlay", () => {
    const pagePath = path.join(
      frontendRoot,
      "src",
      "app",
      "dashboard",
      "transactions",
      "[id]",
      "page.tsx"
    );
    assert.ok(fs.existsSync(pagePath), "transaction detail page.tsx must exist");
    const pageContent = fs.readFileSync(pagePath, "utf-8");

    assert.ok(
      pageContent.includes("data-testid=\"header-ask-clauseguard-btn\""),
      "page.tsx must define data-testid for header Ask ClauseGuard button"
    );
    assert.ok(
      pageContent.includes("setIsAskModalOpen(true)"),
      "Clicking header button must activate isAskModalOpen state"
    );
    assert.ok(
      pageContent.includes("data-testid=\"ask-clauseguard-modal-overlay\""),
      "page.tsx must render modal overlay when isAskModalOpen is true"
    );
    assert.ok(
      pageContent.includes("tab-ask-clauseguard-btn"),
      "page.tsx must define data-testid for tab Ask ClauseGuard button"
    );
    assert.ok(
      pageContent.includes("scrollIntoView"),
      "Tab button must invoke smooth scroll into workspace view"
    );
    assert.ok(
      pageContent.includes("data-testid=\"rag-tab-panel\""),
      "page.tsx must render rag tab panel with data-testid"
    );
  });

  test("4. API client implements queryTransactionRAG and fetchTransactionChunks", () => {
    const apiPath = path.join(frontendRoot, "src", "lib", "api.ts");
    assert.ok(fs.existsSync(apiPath), "src/lib/api.ts must exist");
    const apiContent = fs.readFileSync(apiPath, "utf-8");

    assert.ok(
      apiContent.includes("export async function queryTransactionRAG"),
      "api.ts must export queryTransactionRAG"
    );
    assert.ok(
      apiContent.includes("export async function fetchTransactionChunks"),
      "api.ts must export fetchTransactionChunks"
    );
    assert.ok(
      apiContent.includes("/rag/query"),
      "api.ts must target /rag/query endpoint"
    );
    assert.ok(
      apiContent.includes("/rag/chunks"),
      "api.ts must target /rag/chunks endpoint"
    );
  });
});
