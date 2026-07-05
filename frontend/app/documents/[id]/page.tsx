"use client";

import { useEffect, useState } from "react";
import { use } from "react";
import Link from "next/link";
import { AlertCircle, ArrowLeft, ChevronRight, Loader2 } from "lucide-react";

import Navbar from "@/components/NavBar";
import Sidebar from "@/components/SideBar";
import MetadataCard from "@/components/document/MetadataCard";
import PreviewCard from "@/components/document/PreviewCard";
import AssistantPanel from "@/components/document/AssistantPanel";
import ExtractionCard from "@/components/document/ExtractionCard";
import MatchingPanel from "@/components/document/MatchingPanel";
import { getDocument, DocumentSummary } from "@/lib/api";

export default function DocumentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [doc, setDoc] = useState<DocumentSummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function fetchDoc() {
      try {
        const data = await getDocument(id);
        if (cancelled) return;
        setDoc(data);
        if (data.status === "processing") {
          setTimeout(fetchDoc, 2000);
        }
      } catch (err: any) {
        if (cancelled) return;
        if (err.response?.status === 401) {
          localStorage.removeItem("access_token");
          window.location.reload();
          return;
        }
        setError("Failed to load document.");
      }
    }

    fetchDoc();
    return () => { cancelled = true; };
  }, [id]);

  return (
    <div className="flex bg-slate-100 min-h-screen">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <main className="p-8 space-y-6">

          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Link href="/documents" className="hover:text-blue-600 transition flex items-center gap-1">
              <ArrowLeft size={14} />
              My Documents
            </Link>
            <ChevronRight size={14} />
            <span className="text-gray-800 font-medium truncate max-w-xs">
              {doc?.filename ?? "Loading…"}
            </span>
          </div>

          {/* Loading */}
          {!doc && !error && (
            <div className="flex items-center justify-center py-32">
              <Loader2 className="animate-spin text-blue-600" size={40} />
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-2xl p-6 flex items-center gap-3 text-sm">
              <AlertCircle size={20} className="shrink-0" />
              {error}
            </div>
          )}

          {/* Processing */}
          {doc?.status === "processing" && (
            <div className="bg-white border shadow-sm rounded-3xl flex flex-col items-center justify-center py-24 gap-4">
              <Loader2 className="animate-spin text-blue-600" size={48} />
              <h2 className="text-xl font-semibold">Analysis in progress…</h2>
              <p className="text-gray-400 text-sm">This page will update automatically.</p>
            </div>
          )}

          {/* Failed */}
          {doc?.status === "failed" && (
            <div className="bg-red-50 border border-red-200 rounded-3xl p-8 space-y-3">
              <div className="flex items-center gap-3 text-red-700">
                <AlertCircle size={24} />
                <h2 className="text-xl font-semibold">Processing Failed</h2>
              </div>
              {doc.error && (
                <p className="text-sm text-red-600 font-mono bg-red-100 rounded-xl p-4">
                  {doc.error}
                </p>
              )}
              <Link
                href="/documents"
                className="inline-flex items-center gap-2 text-sm font-semibold text-red-600 hover:underline mt-2"
              >
                <ArrowLeft size={14} />
                Back to My Documents
              </Link>
            </div>
          )}

          {/* Done */}
          {doc?.status === "done" && (
            <div className="space-y-6">
              <div>
                <h1 className="text-3xl font-bold truncate">{doc.filename}</h1>
              </div>

              <MetadataCard
                metadata={{
                  language: doc.language ?? undefined,
                  languageCode: doc.language ?? undefined,
                  pages: doc.pages ?? undefined,
                  characters: doc.characters ?? undefined,
                  ocrUsed: doc.ocr_used,
                }}
              />

              <ExtractionCard
                documentId={doc.id}
                hasText={!!doc.extracted_text}
              />

              <div className="grid grid-cols-1 xl:grid-cols-[1fr_400px] gap-6 items-start">
                <PreviewCard
                  documentId={doc.id}
                  filename={doc.filename}
                  summary={doc.summary ?? undefined}
                  preview={doc.extracted_text ?? ""}
                  translatedText={doc.translated_text ?? undefined}
                />
                <div className="space-y-6">
                  <AssistantPanel
                    documentId={doc.id}
                    hasText={!!doc.extracted_text}
                  />
                  <MatchingPanel
                    documentId={doc.id}
                    hasText={!!doc.extracted_text}
                  />
                </div>
              </div>
            </div>
          )}

        </main>
      </div>
    </div>
  );
}
