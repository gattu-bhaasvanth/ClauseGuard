export interface RAGCitation {
  documentId: string;
  documentName: string;
  documentType: string;
  pageNumber: number;
  clauseNumber?: string | null;
  clauseTitle?: string | null;
  excerpt: string;
  relevanceScore: number;
}

export interface RAGQueryRequest {
  query: string;
  topK?: number;
}

export interface RAGQueryResponse {
  query: string;
  answer: string;
  grounded: boolean;
  status: "GROUNDED" | "INSUFFICIENT_EVIDENCE";
  confidence: number;
  citations: RAGCitation[];
  bundleId: string;
  disclaimer: string;
}

export interface ChunkItem {
  id: string;
  bundleId: string;
  documentId: string;
  pageNumber: number;
  clauseNumber?: string | null;
  clauseTitle?: string | null;
  chunkType: string;
  chunkText: string;
  hasEmbedding: boolean;
  createdAt: string;
}
