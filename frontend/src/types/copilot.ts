import { SeverityLevel } from "./transaction";

export type DateCertaintyType =
  | "CONTRACTUAL"
  | "INFERRED"
  | "MARKETING"
  | "CONFLICTING"
  | "UNCERTAIN";

export type TimelineEventStatus = "PAST" | "UPCOMING" | "TENTATIVE";

export interface RiskVectorItem {
  id: string;
  name: string;
  score: number; // 0-100
  riskLevel: SeverityLevel;
  primaryConcern: string;
  quantifiedStat?: string;
  findingIds: string[];
}

export interface FinancialExposureBreakdown {
  totalFinancialAtRisk: number;
  totalFinancialAtRiskFormatted: string;
  baseConsideration: number;
  baseConsiderationFormatted: string;
  earnestMoneyForfeitRisk: number;
  earnestMoneyForfeitRiskFormatted: string;
  statutoryForfeitLimit: number;
  statutoryForfeitLimitFormatted: string;
  excessForfeitExposure: number;
  excessForfeitExposureFormatted: string;
  delayInterestRateBuyer: number;
  delayCompensationRateDeveloper: number;
  monthlyAsymmetryCost: number;
  monthlyAsymmetryCostFormatted: string;
  areaDiscrepancyCostImpact: number;
  areaDiscrepancyCostImpactFormatted: string;
}

export interface PriorityActionItem {
  id: string;
  title: string;
  category: "NEGOTIATION" | "DOCUMENT_REQUEST" | "LEGAL_REVIEW" | "PAYMENT_HOLD";
  severity: SeverityLevel;
  description: string;
  clauseReference?: string;
  documentName?: string;
  recommendedAction: string;
}

export interface TransactionCommandCenterData {
  bundleId: string;
  projectName: string;
  unitNumber: string;
  developerName: string;
  healthScore: number;
  riskLevel: string;
  financialExposure: FinancialExposureBreakdown;
  riskVectors: RiskVectorItem[];
  priorityActions: PriorityActionItem[];
  missingDocumentsCount: number;
  totalDocumentsCount: number;
  totalClausesAnalyzed: number;
  totalFindingsCount: number;
}

export interface CopilotCitation {
  documentId: string;
  documentName: string;
  documentType: string;
  pageNumber: number;
  clauseNumber?: string;
  clauseTitle?: string;
  excerpt: string;
  relevanceScore: number;
}

export interface CopilotChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  intent?: string;
  grounded?: boolean;
  refused?: boolean;
  confidence?: number;
  citations?: CopilotCitation[];
  suggestedNextQuestions?: string[];
}

export interface CopilotQueryRequest {
  query: string;
  topK?: number;
}

export interface CopilotQueryResponse {
  query: string;
  answer: string;
  grounded: boolean;
  refused: boolean;
  intent: string;
  confidence: number;
  citations: CopilotCitation[];
  bundleId: string;
  suggestedNextQuestions: string[];
  disclaimer: string;
}

export interface ExplainableRiskLineage {
  documentName: string;
  pageNumber: number;
  clauseNumber?: string;
  clauseTitle?: string;
  findingId: string;
  verbatimExcerpt: string;
}

export interface ExplainableRiskData {
  findingId: string;
  title: string;
  severity: SeverityLevel;
  category: string;
  plainEnglishHarm: string;
  statutoryBenchmark: string;
  quantifiedImpact: string;
  lineage: ExplainableRiskLineage;
  primaryEvidence: Record<string, any>;
  secondaryEvidence?: Record<string, any>;
  recommendedNegotiationScript: string;
}

export interface TimelineEvent {
  id: string;
  title: string;
  eventDate?: string;
  dateType: DateCertaintyType;
  status: TimelineEventStatus;
  description: string;
  documentName?: string;
  pageNumber?: number;
  clauseReference?: string;
  linkedObligationAmount?: number;
  linkedObligationFormatted?: string;
  conflictingDate?: string;
  conflictDetails?: string;
  precision?: "DAY" | "MONTH" | "YEAR" | "UNCERTAIN" | string;
  rawEvidence?: string;
  isDerived?: boolean;
  sourceDocument?: string;
}

export interface TimelineData {
  bundleId: string;
  events: TimelineEvent[];
  totalEvents: number;
  conflictingEventsCount: number;
  contractualEventsCount: number;
  marketingEventsCount: number;
  inferredEventsCount: number;
  uncertainEventsCount: number;
  conflictSummary?: string;
}

export interface BriefSection {
  sectionNumber: number;
  sectionKey: string;
  title: string;
  summary: string;
  bulletPoints: string[];
  evidenceLineage: Array<{
    document: string;
    page?: number;
    clause?: string;
    excerpt: string;
  }>;
}

export interface TransactionBriefData {
  briefId: string;
  bundleId: string;
  generatedAt: string;
  project: string;
  unit: string;
  developer: string;
  healthScore: number;
  riskLevel: string;
  totalFinancialExposure: string;
  sections: BriefSection[];
  disclaimer: string;
}
