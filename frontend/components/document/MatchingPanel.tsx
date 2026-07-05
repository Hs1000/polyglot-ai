"use client";

import { useState } from "react";
import { Target, Loader2, CheckCircle2, AlertCircle, XCircle, Info } from "lucide-react";
import { matchDocument, MatchResult, MatchStatus } from "@/lib/api";

interface Props {
  documentId: string;
  hasText: boolean;
}

const STATUS_CONFIG: Record<MatchStatus, {
  icon: React.ReactNode;
  label: string;
  row: string;
  badge: string;
}> = {
  match: {
    icon: <CheckCircle2 size={16} className="text-green-500 shrink-0" />,
    label: "Match",
    row: "bg-green-50",
    badge: "bg-green-100 text-green-700",
  },
  partial: {
    icon: <AlertCircle size={16} className="text-amber-500 shrink-0" />,
    label: "Partial",
    row: "bg-amber-50",
    badge: "bg-amber-100 text-amber-700",
  },
  missing: {
    icon: <XCircle size={16} className="text-red-500 shrink-0" />,
    label: "Missing",
    row: "bg-red-50",
    badge: "bg-red-100 text-red-700",
  },
  not_specified: {
    icon: <Info size={16} className="text-gray-400 shrink-0" />,
    label: "Not in JD",
    row: "bg-slate-50",
    badge: "bg-slate-100 text-slate-500",
  },
};

function ScoreRing({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 75 ? "text-green-600" :
    pct >= 50 ? "text-amber-500" :
                "text-red-500";
  return (
    <div className={`flex flex-col items-center justify-center w-20 h-20 rounded-full border-4 ${
      pct >= 75 ? "border-green-200" : pct >= 50 ? "border-amber-200" : "border-red-200"
    } shrink-0`}>
      <span className={`text-2xl font-bold leading-none ${color}`}>{pct}%</span>
      <span className="text-xs text-gray-400 mt-0.5">match</span>
    </div>
  );
}

export default function MatchingPanel({ documentId, hasText }: Props) {
  const [jd, setJd]           = useState("");
  const [result, setResult]   = useState<MatchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  async function handleMatch() {
    if (!jd.trim() || !hasText || loading) return;
    setLoading(true);
    setError("");
    try {
      const data = await matchDocument(documentId, jd);
      setResult(data);
    } catch (err: any) {
      if (err?.response?.status === 401) {
        localStorage.removeItem("access_token");
        window.location.reload();
        return;
      }
      setError(err?.response?.data?.detail || "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  // Separate comparison rows from purely informational fields (Role Title, Key Skills)
  const INFO_FIELDS = new Set(["Role Title", "Key Skills Required"]);
  const scored = result?.comparisons.filter(c => !INFO_FIELDS.has(c.field)) ?? [];
  const info   = result?.comparisons.filter(c =>  INFO_FIELDS.has(c.field)) ?? [];

  return (
    <div className="bg-white rounded-3xl border shadow-sm">

      {/* Header */}
      <div className="p-5 flex items-center gap-3 border-b">
        <div className="bg-rose-100 rounded-xl p-2.5 shrink-0">
          <Target className="text-rose-600" size={20} />
        </div>
        <div>
          <h2 className="text-base font-bold leading-tight">JD Match Analyzer</h2>
          <p className="text-gray-500 text-xs mt-0.5">
            Paste a job description to see how well this resume fits
          </p>
        </div>
      </div>

      {/* JD input */}
      <div className="p-5 space-y-3">
        <textarea
          className="w-full resize-none border rounded-2xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 disabled:opacity-50 placeholder:text-gray-300"
          rows={6}
          placeholder="Paste the job description here…"
          value={jd}
          disabled={loading}
          onChange={e => setJd(e.target.value)}
        />
        <button
          onClick={handleMatch}
          disabled={!hasText || loading || !jd.trim()}
          className="w-full bg-rose-600 hover:bg-rose-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold py-2.5 rounded-2xl transition flex items-center justify-center gap-2"
        >
          {loading
            ? <><Loader2 size={15} className="animate-spin" /> Analyzing…</>
            : result ? "Re-analyze" : "Analyze Match"}
        </button>
        {error && (
          <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-xl px-3 py-2">
            {error}
          </p>
        )}
      </div>

      {/* Results */}
      {result && (
        <div className="border-t px-5 pb-5 space-y-5">

          {/* Score summary */}
          {(() => {
            const countMatch   = scored.filter(c => c.status === "match").length;
            const countPartial = scored.filter(c => c.status === "partial").length;
            const countMissing = scored.filter(c => c.status === "missing").length;
            return (
              <div className="flex items-center gap-5 pt-4">
                <ScoreRing score={result.match_score} />
                <div className="grid grid-cols-3 gap-2 flex-1">
                  {[
                    { label: "Matched", value: countMatch,   color: "text-green-600 bg-green-50 border-green-100" },
                    { label: "Partial", value: countPartial, color: "text-amber-600 bg-amber-50 border-amber-100" },
                    { label: "Missing", value: countMissing, color: "text-red-600 bg-red-50 border-red-100" },
                  ].map(({ label, value, color }) => (
                    <div key={label} className={`rounded-2xl border p-2 text-center ${color}`}>
                      <p className="text-xl font-bold leading-none">{value}</p>
                      <p className="text-xs mt-0.5 font-medium">{label}</p>
                    </div>
                  ))}
                </div>
              </div>
            );
          })()}

          {/* Field-by-field comparison */}
          <div className="space-y-2">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
              Requirement breakdown
            </p>
            <div className="rounded-2xl border overflow-hidden divide-y">
              {scored.map(c => {
                const cfg = STATUS_CONFIG[c.status];
                const isNotSpec = c.status === "not_specified";
                return (
                  <div key={c.field} className={`px-4 py-3 ${cfg.row}`}>
                    <div className="flex items-start gap-2">
                      {cfg.icon}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`text-sm font-semibold ${isNotSpec ? "text-gray-500" : "text-gray-800"}`}>
                            {c.field}
                          </span>
                          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${cfg.badge}`}>
                            {cfg.label}
                          </span>
                        </div>
                        {isNotSpec ? (
                          <div className="mt-1.5 text-xs text-gray-400">
                            {c.resume_value
                              ? <><span className="text-gray-400">Resume has: </span><span className="text-gray-600">{c.resume_value}</span></>
                              : "Not mentioned in job description"}
                          </div>
                        ) : (
                          <>
                            {c.detail && (
                              <p className="text-xs text-gray-500 mt-1 leading-snug">{c.detail}</p>
                            )}
                            <div className="mt-1.5 grid grid-cols-2 gap-2 text-xs">
                              {c.jd_value && (
                                <div>
                                  <span className="text-gray-400">Required: </span>
                                  <span className="text-gray-700">{c.jd_value}</span>
                                </div>
                              )}
                              {c.resume_value && (
                                <div>
                                  <span className="text-gray-400">Resume: </span>
                                  <span className="text-gray-700">{c.resume_value}</span>
                                </div>
                              )}
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Informational fields (Role Title, Key Skills) */}
          {info.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
                Job details
              </p>
              <div className="rounded-2xl border overflow-hidden divide-y bg-slate-50">
                {info.map(c => c.jd_value && (
                  <div key={c.field} className="px-4 py-3">
                    <p className="text-xs text-gray-400 font-medium uppercase tracking-wide">{c.field}</p>
                    <p className="text-sm text-gray-700 mt-0.5">{c.jd_value}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
