"use client";

export interface DocumentActivity {
  id: string;
  filename: string;
  fileSize?: number | null;
  status: "completed" | "failed";
  language?: string | null;
  languageCode?: string | null;
  pages?: number | null;
  characters?: number | null;
  ocrUsed?: boolean | null;
  summary?: string | null;
  preview?: string | null;
  translatedText?: string | null;
  createdAt: string;
}

const CURRENT_DOCUMENT_KEY = "polyglot_current_document";
export const CURRENT_DOCUMENT_EVENT = "polyglot-current-document";

function canUseStorage() {
  return typeof window !== "undefined" && Boolean(window.localStorage);
}

export function getCurrentDocument(): DocumentActivity | null {
  if (!canUseStorage()) return null;

  try {
    const raw = window.localStorage.getItem(CURRENT_DOCUMENT_KEY);
    if (!raw) return null;

    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : null;
  } catch {
    return null;
  }
}

export function saveCurrentDocument(item: DocumentActivity) {
  if (!canUseStorage()) return;

  window.localStorage.setItem(CURRENT_DOCUMENT_KEY, JSON.stringify(item));
  window.dispatchEvent(new Event(CURRENT_DOCUMENT_EVENT));
}

export function clearCurrentDocument() {
  if (!canUseStorage()) return;

  window.localStorage.removeItem(CURRENT_DOCUMENT_KEY);
  window.dispatchEvent(new Event(CURRENT_DOCUMENT_EVENT));
}

export function clearAppStorage() {
  if (!canUseStorage()) return;

  window.localStorage.removeItem(CURRENT_DOCUMENT_KEY);
  window.dispatchEvent(new Event(CURRENT_DOCUMENT_EVENT));
}
