/**
 * Phase 9 Domain-Specific Clause Intelligence TypeScript Definitions
 */

export interface AlternativePrediction {
  category: string;
  probability: number;
}

export interface RiskAnalysisSummary {
  status: string;
  severity?: string;
  analysis_summary: string;
  risk_details?: string;
}

export interface ClassifyResponse {
  primary_category: string;
  confidence: number;
  classification_source: string;
  model_version?: string;
  dataset_version?: string;
  top_alternatives: AlternativePrediction[];
  explanation_notes?: string;
  risk_analysis: RiskAnalysisSummary;
}

export interface CandidateMetric {
  id: string;
  name: string;
  accuracy: number;
  macro_f1: number;
  weighted_f1: number;
  ece_calibration_error: number;
  latency_ms: number;
  model_size_kb: number;
  delta_f1: number;
}

export interface BenchmarkComparison {
  evaluation_timestamp: string;
  test_samples_evaluated: number;
  candidates: CandidateMetric[];
  selected_model: string;
  selected_model_name: string;
  baseline_macro_f1: number;
  selected_macro_f1: number;
  improvement_delta_f1: number;
  promotion_gate_passed: boolean;
  justification: string;
}

export interface EngineStatus {
  active_engine: string;
  model_name: string;
  model_version: string;
  dataset_version: string;
  fallback_available: boolean;
  benchmark_latency_ms: number;
  baseline_macro_f1: number;
  current_macro_f1: number;
  improvement_delta_f1: number;
  num_categories: number;
  categories: string[];
}

export interface EnhancedClause {
  id: string;
  clauseNumber: string;
  title: string;
  category: string;
  status: string;
  severity?: string;
  obligationType?: string;
  pageNumber: number;
  previewText: string;
  fullExcerpt: string;
  analysisSummary: string;
  riskDetails?: string;
  confidence?: number;
  classificationSource?: "ML_TRANSFORMER" | "DETERMINISTIC_HEURISTIC" | string;
  modelVersion?: string;
  datasetVersion?: string;
  topAlternatives?: AlternativePrediction[];
  explanationNotes?: string;
}
