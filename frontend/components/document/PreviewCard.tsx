"use client";

import { useState } from "react";
import { Copy, Download, Eye, Languages, Loader2, Sparkles } from "lucide-react";
import { exportDocumentPdf } from "@/lib/api";

interface PreviewCardProps {
  documentId?: string;
  filename?: string;
  summary?: string;
  preview: string;
  translatedText?: string;
}

export default function PreviewCard({
  documentId,
  filename = "document",
  summary,
  preview,
  translatedText,
}: PreviewCardProps) {
  const [downloading, setDownloading] = useState(false);

  async function copyText() {
    const text = summary || translatedText || preview;
    if (!text) return;
    await navigator.clipboard.writeText(text);
  }

  async function handleDownload() {
    if (!documentId || downloading) return;
    setDownloading(true);
    try {
      await exportDocumentPdf(documentId, filename);
    } catch (err: any) {
      if (err?.response?.status === 401) {
        localStorage.removeItem("access_token");
        window.location.reload();
      }
    } finally {
      setDownloading(false);
    }
  }

  function renderText(text: string) {
    return text
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0)
      .map((line, i) => {
        const isBullet = line.startsWith("•") || line.startsWith("-");
        const isHeading =
          !isBullet &&
          line.length < 60 &&
          /[a-z]/.test(line) &&
          /^[A-Z]/.test(line) &&
          !line.endsWith(".");

        return (
          <p
            key={i}
            className={
              isHeading
                ? "font-semibold text-gray-900 mt-4 first:mt-0"
                : isBullet
                ? "pl-4 text-gray-600"
                : "text-gray-700"
            }
          >
            {line}
          </p>
        );
      });
  }

  const hasTranslation = Boolean(translatedText && translatedText !== preview);
  const hasContent = Boolean(summary || translatedText || preview);
  const canDownload = Boolean(documentId && (hasTranslation || preview));

  return (
    <div className="bg-white rounded-3xl border shadow-sm">

      {/* Header */}
      <div className="flex items-center justify-between border-b p-6">
        <div className="flex items-center gap-3">
          <Eye className="text-blue-600" size={22} />
          <h2 className="text-2xl font-bold">Document Preview</h2>
        </div>

        <div className="flex gap-3">
          <button
            onClick={copyText}
            disabled={!hasContent}
            className="flex items-center gap-2 bg-slate-100 hover:bg-slate-200 disabled:opacity-50 px-4 py-2 rounded-xl transition text-sm"
          >
            <Copy size={16} />
            Copy
          </button>

          <button
            onClick={handleDownload}
            disabled={!canDownload || downloading}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl transition text-sm font-medium"
          >
            {downloading
              ? <><Loader2 size={16} className="animate-spin" /> Generating…</>
              : <><Download size={16} /> Download PDF</>
            }
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="p-6 space-y-6">

        {!hasContent ? (
          <div className="text-center py-20">
            <Eye className="mx-auto text-gray-300 mb-4" size={48} />
            <h3 className="text-xl font-semibold">No Preview Available</h3>
            <p className="text-gray-500 mt-2">
              Upload a document to generate an AI summary.
            </p>
          </div>
        ) : (
          <>
            {summary && (
              <div className="bg-blue-50 border border-blue-100 rounded-2xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className="text-blue-600" size={18} />
                  <span className="text-sm font-semibold text-blue-700 uppercase tracking-wide">
                    AI Summary
                  </span>
                </div>
                <div className="space-y-1.5 text-sm leading-relaxed">
                  {renderText(summary)}
                </div>
              </div>
            )}

            {hasTranslation && (
              <div className="border rounded-2xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <Languages className="text-emerald-600" size={18} />
                  <span className="text-sm font-semibold text-emerald-700 uppercase tracking-wide">
                    English Translation
                  </span>
                </div>
                <div className="max-h-80 overflow-auto space-y-1.5 text-sm leading-relaxed">
                  {renderText(translatedText || "")}
                </div>
              </div>
            )}

            {!summary && preview && (
              <div className="text-center py-16">
                <Sparkles className="mx-auto text-gray-300 mb-4" size={44} />
                <h3 className="text-xl font-semibold">Summary Unavailable</h3>
                <p className="text-gray-500 mt-2">
                  Text was extracted, but a summary was not generated for this document.
                </p>
              </div>
            )}
          </>
        )}

      </div>
    </div>
  );
}
