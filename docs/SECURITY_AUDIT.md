# ClauseGuard Security & Isolation Architecture

## 1. Security Philosophy & Scope

ClauseGuard is designed with a defense-in-depth security posture suitable for sensitive property contracts. Security checks were performed for the tested project scope.

> **Scope Notice**: Security checks passed for the tested scope. ClauseGuard is an informational transaction intelligence tool designed to operate locally with zero cloud leakage of confidential contracts.

---

## 2. Key Security Mechanisms

### A. Document Upload Armor
- **Allowed MIME & Extensions**: Whitelisted strictly to `.pdf`, `.png`, `.jpg`, `.jpeg`. Executables, archives, and unknown binaries are rejected with `HTTP 400 Bad Request`.
- **Magic Byte Verification**: PDFs must start with `%PDF` magic bytes. Non-PDF files disguised with `.pdf` extensions are blocked before ingestion.
- **Maximum File Size**: Strict 50 MB ceiling (`HTTP 413 Request Entity Too Large`).
- **Empty File Protection**: 0-byte uploads are rejected with `HTTP 400 Bad Request`.
- **Path Traversal Prevention**: Storage paths are sanitized using `Path(original_filename).name`, stripping directory traversal characters (`../../`), and stored using SHA-256 content hashes in `data/uploads/`.

### B. Transaction & Tenant Isolation (IDOR Defense)
- **Bundle Scoping**: Every document, clause, page, metadata attribute, discrepancy finding, risk vector, and vector chunk is strictly partitioned by `bundle_id == transaction_id`.
- **Query Verification**: Route handlers execute `_get_verified_document(db, transaction_id, document_id)`. Accessing a foreign document belonging to another transaction bundle returns `HTTP 404 Not Found`.
- **Vector Isolation**: RAG embeddings and chunk searches explicitly include `where(DocumentChunk.bundle_id == bundle_id)`, guaranteeing that semantic search cannot leak text across transaction boundaries.

### C. Input Validation & SQL Injection Prevention
- **Pydantic v2 Schemas**: All incoming REST payloads undergo strict type validation. Malformed or extra inputs are rejected with standard HTTP 422 errors.
- **SQLAlchemy 2.0 Async ORM**: All database queries are compiled into parameterized SQL statements. Zero string interpolation is used in query building.

### D. Security Headers
A dedicated Starlette/FastAPI middleware injects defensive headers on all HTTP responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

### E. AI / ML / RAG Grounding & Privacy
- **Local In-Process Inference**: Vector embeddings (`all-MiniLM-L6-v2`) and clause classification models run 100% on the local CPU via ONNX Runtime. Zero document text or embeddings are transmitted to external AI APIs.
- **Strict Grounding Contract**: The RAG engine enforces a minimum confidence threshold ($0.28$). When evidence is absent, the system explicitly refuses to speculate with `status: "INSUFFICIENT_EVIDENCE"`.
- **Traceable Provenance**: All answers return clickable citation chips detailing `Document → Page → Clause → Raw Excerpt`.

### F. Environment & Secrets Management
- All secrets are loaded via environment variables (`.env`).
- `.gitignore` strictly excludes `.env`, `.env.*`, certificates (`*.pem`, `*.key`), database binaries (`*.db`, `*.sqlite`), and uploaded files (`data/uploads/*`).
- Zero API keys, passwords, or credentials are hardcoded in the codebase.
