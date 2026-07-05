"use client";

import { useState } from "react";
import { Sparkles, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { extractDocument, ExtractionResult } from "@/lib/api";

const TYPE_LABELS: Record<string, string> = {
  resume:   "Resume / CV",
  invoice:  "Invoice",
  contract: "Contract",
  research: "Research Paper",
  report:   "Report",
  general:  "General Document",
};

const TYPE_COLORS: Record<string, string> = {
  resume:   "bg-blue-100 text-blue-700",
  invoice:  "bg-green-100 text-green-700",
  contract: "bg-purple-100 text-purple-700",
  research: "bg-orange-100 text-orange-700",
  report:   "bg-teal-100 text-teal-700",
  general:  "bg-gray-100 text-gray-700",
};

// Fields whose values tend to be long get a full-width card
const WIDE_FIELDS = new Set([
  "Programming Languages",
  "Frameworks",
  "Databases & Tools",
  "Key Points",
  "Abstract",
  "Results",
  "Conclusion",
  "Methodology",
  "Summary",
  "Key Findings",
  "Parties",
]);

interface Props {
  documentId: string;
  hasText: boolean;
}

export default function ExtractionCard({ documentId, hasText }: Props) {
  const [result, setResult]       = useState<ExtractionResult | null>(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState("");
  const [collapsed, setCollapsed] = useState(false);

  async function handleExtract() {
    if (!hasText || loading) return;
    setLoading(true);
    setError("");
    try {
      const data = await extractDocument(documentId);
      setResult(data);
    } catch (err: any) {
      if (err?.response?.status === 401) {
        localStorage.removeItem("access_token");
        window.location.reload();
        return;
      }
      setError(err?.response?.data?.detail || "Extraction failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  const entries = result ? Object.entries(result.fields) : [];
  const filled  = entries.filter(([, v]) => v).length;

  return (
    <div className="bg-white rounded-3xl border shadow-sm">

      {/* Header */}
      <div className="p-5 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="bg-purple-100 rounded-xl p-2.5 shrink-0">
            <Sparkles className="text-purple-600" size={20} />
          </div>
          <div className="min-w-0">
            <h2 className="text-base font-bold leading-tight">Smart Extraction</h2>
            <p className="text-gray-500 text-xs mt-0.5">
              {result
                ? `${filled} of ${entries.length} fields extracted`
                : "Auto-detect type and pull key fields"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {result && (
            <button
              onClick={() => setCollapsed((c) => !c)}
              className="text-gray-400 hover:text-gray-600 p-1 rounded-lg"
            >
              {collapsed ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
            </button>
          )}
          <button
            onClick={handleExtract}
            disabled={!hasText || loading}
            className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-semibold px-3 py-2 rounded-xl transition flex items-center gap-1.5 whitespace-nowrap"
          >
            {loading ? (
              <><Loader2 size={13} className="animate-spin" /> Extracting…</>
            ) : result ? "Re-run" : "Extract"}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mx-5 mb-4 text-xs text-red-600 bg-red-50 border border-red-200 rounded-xl px-3 py-2">
          {error}
        </div>
      )}

      {/* Results */}
      {result && !collapsed && (
        <div className="border-t px-5 pb-5">

          {/* Document type badge */}
          <div className="flex items-center gap-2 mt-4 mb-4">
            <span className="text-xs text-gray-400 font-medium">Detected type</span>
            <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${
              TYPE_COLORS[result.document_type] ?? TYPE_COLORS.general
            }`}>
              {TYPE_LABELS[result.document_type] ?? result.document_type}
            </span>
          </div>

          {/* Field cards grid */}
          <div className="grid grid-cols-2 gap-2">
            {entries.map(([label, value]) => (
              <div
                key={label}
                className={`bg-slate-50 rounded-2xl p-3 flex flex-col gap-1 ${
                  WIDE_FIELDS.has(label) ? "col-span-2" : ""
                }`}
              >
                <span className="text-xs text-gray-400 font-medium uppercase tracking-wide leading-none">
                  {label}
                </span>
                <span className={`text-sm leading-snug break-words ${
                  value ? "text-gray-800 font-medium" : "text-gray-300 italic font-normal"
                }`}>
                  {value ?? "Not found"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && (
        <div className="px-5 pb-5 text-center">
          <p className="text-xs text-gray-400">
            {hasText
              ? "Click Extract to automatically pull key information from this document."
              : "Available once document processing is complete."}
          </p>
        </div>
      )}

    </div>
  );
}
