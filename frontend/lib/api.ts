import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function loginUser(email: string, password: string): Promise<void> {
  const res = await api.post("/api/v1/auth/login", { email, password });
  localStorage.setItem("access_token", res.data.access_token);
}

export async function registerUser(name: string, email: string, password: string): Promise<void> {
  await api.post("/api/v1/auth/register", { name, email, password });
  await loginUser(email, password);
}

export async function uploadFile(file: File): Promise<{ document_id: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post("/api/v1/upload/", form);
  return res.data;
}

export async function getDocumentStatus(id: string) {
  const res = await api.get(`/api/v1/upload/${id}`);
  return res.data;
}

export interface DocumentSummary {
  id: string;
  filename: string;
  status: "processing" | "done" | "failed";
  language: string | null;
  pages: number | null;
  characters: number | null;
  ocr_used: boolean;
  summary: string | null;
  translated_text: string | null;
  extracted_text: string | null;
  error: string | null;
  created_at: string;
}

export async function getMyDocuments(): Promise<DocumentSummary[]> {
  const res = await api.get("/api/v1/documents/");
  return res.data;
}

export async function getDocument(id: string): Promise<DocumentSummary> {
  const res = await api.get(`/api/v1/documents/${id}`);
  return res.data;
}

export async function deleteDocument(id: string): Promise<void> {
  await api.delete(`/api/v1/documents/${id}`);
}

export interface TranslationResult {
  source_language: string;
  target_language: string;
  translated_text: string;
  translation_available: boolean;
}

export async function translateText(
  text: string,
  sourceLanguage = "auto",
  targetLanguage = "en",
): Promise<TranslationResult> {
  const res = await api.post("/api/v1/translate/", {
    text,
    source_language: sourceLanguage,
    target_language: targetLanguage,
  });
  return res.data;
}

// ── Extraction ────────────────────────────────────────────────────────────────

export interface ExtractionResult {
  document_type: string;
  fields: Record<string, string | null>;
}

export async function extractDocument(id: string): Promise<ExtractionResult> {
  const res = await api.post(`/api/v1/documents/${id}/extract`);
  return res.data;
}

// ── Matching ──────────────────────────────────────────────────────────────────

export type MatchStatus = "match" | "partial" | "missing" | "not_specified";

export interface FieldComparison {
  field: string;
  jd_value: string | null;
  resume_value: string | null;
  status: MatchStatus;
  detail: string | null;
}

export interface MatchResult {
  match_score: number;
  matched: number;
  partial: number;
  missing: number;
  comparisons: FieldComparison[];
}

export async function matchDocument(id: string, jobDescription: string): Promise<MatchResult> {
  const res = await api.post(`/api/v1/documents/${id}/match`, {
    job_description: jobDescription,
  });
  return res.data;
}

// ── Chat ──────────────────────────────────────────────────────────────────────

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export async function chatWithDocument(
  id: string,
  message: string,
  history: ChatMessage[],
): Promise<string> {
  const res = await api.post(`/api/v1/documents/${id}/chat`, { message, history });
  return res.data.response;
}

// ── Export ────────────────────────────────────────────────────────────────────

export async function exportDocumentPdf(id: string, filename: string): Promise<void> {
  const res = await api.get(`/api/v1/documents/${id}/export/pdf`, {
    responseType: "blob",
  });
  const url = URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename.replace(/\.[^.]+$/, "") + "_translated.pdf";
  a.click();
  URL.revokeObjectURL(url);
}

export async function exportTextPdf(
  text: string,
  title: string,
  label: string,
): Promise<void> {
  const res = await api.post(
    "/api/v1/export/text-pdf",
    { text, title, label },
    { responseType: "blob" },
  );
  const url = URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = title.replace(/\s+/g, "_") + ".pdf";
  a.click();
  URL.revokeObjectURL(url);
}
