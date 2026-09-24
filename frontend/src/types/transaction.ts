export type SeverityLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type FindingType =
  | "INCONSISTENCY"
  | "RISK"
  | "REVIEW_REQUIRED"
  | "INFORMATION"
  | "VERIFIED";

export type DocumentType =
  | "BUILDER_BUYER_AGREEMENT"
  | "SALE_AGREEMENT"
  | "ALLOTMENT_LETTER"
  | "PAYMENT_SCHEDULE"
  | "PROJECT_BROCHURE"
  | "NOC_SANCTION_PLAN"
  | "OTHER";

export interface EvidenceCitation {
  documentId: string;
  documentName: string;
  documentType: DocumentType;
  pageNumber: number;
  clauseNumber?: string;
  excerpt: string;
  boundingBox?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface InconsistencyFinding {
  id: string;
  title: string;
  field: string;
  category: "AREA" | "POSSESSION" | "PRICING" | "PAYMENT" | "PARTY" | "SPECIFICATION";
  severity: SeverityLevel;
  description: string;
  primaryEvidence: EvidenceCitation;
  secondaryEvidence: EvidenceCitation;
  detectedAt: string;
  verified?: boolean;
}

export interface RiskFinding {
  id: string;
  title: string;
  clauseType: string;
  severity: SeverityLevel;
  impact: string;
  explanation: string;
  citation: EvidenceCitation;
  recommendationNote: string;
}

export interface ClauseItem {
  id: string;
  clauseNumber: string;
  title: string;
  category: string;
  status: FindingType;
  severity?: SeverityLevel;
  pageNumber: number;
  previewText: string;
  fullExcerpt: string;
  analysisSummary: string;
  riskDetails?: string;
  confidence?: number;
  classificationSource?: "ML_TRANSFORMER" | "DETERMINISTIC_RULES" | "LLM_FALLBACK" | string;
  modelVersion?: string;
  datasetVersion?: string;
  topAlternatives?: Array<{ category: string; probability: number }>;
  explanationNotes?: string;
}

export interface TransactionDocument {
  id: string;
  fileName: string;
  documentType: DocumentType;
  fileSize: string;
  pageCount: number;
  uploadedAt: string;
  ocrStatus: "COMPLETED" | "NOT_REQUIRED" | "PROCESSING" | "FAILED";
  clauseCount: number;
  issueCount: number;
}

export interface ImportantDate {
  id: string;
  title: string;
  date: string;
  sourceDoc: string;
  isMilestone: boolean;
  status: "UPCOMING" | "PAST" | "TENTATIVE";
  description: string;
}

export interface PaymentObligation {
  id: string;
  milestoneTitle: string;
  percentage: number;
  amount: number;
  dueDateCondition: string;
  status: "PENDING" | "PAID" | "DISPUTED";
  clauseCitation: string;
}

export interface PropertySummary {
  project: string;
  developer: string;
  unit: string;
  floor: number;
  tower: string;
  carpetAreaSqFt: number;
  superAreaSqFt: number;
  advertisedCarpetAreaSqFt?: number;
  salePrice: number;
  possessionDate: string;
  gracePeriodMonths: number;
  location: string;
}

export interface Transaction {
  id: string;
  title: string;
  property: PropertySummary;
  healthScore: number;
  status: "ANALYSIS_COMPLETE" | "IN_PROGRESS" | "DRAFT" | "NEEDS_ATTENTION";
  documentsCount: number;
  issuesCount: number;
  inconsistenciesCount: number;
  risksCount: number;
  importantDatesCount: number;
  paymentObligationsCount: number;
  documents: TransactionDocument[];
  inconsistencies: InconsistencyFinding[];
  risks: RiskFinding[];
  importantDates: ImportantDate[];
  paymentObligations: PaymentObligation[];
  clauses: ClauseItem[];
  createdAt: string;
  updatedAt: string;
}
