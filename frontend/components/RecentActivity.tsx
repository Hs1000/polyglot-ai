"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AlertCircle, ArrowRight, CheckCircle2, FileText } from "lucide-react";

import { getMyDocuments, DocumentSummary } from "@/lib/api";

function formatDate(iso: string) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(iso));
}

export default function RecentActivity() {
  const [docs, setDocs] = useState<DocumentSummary[]>([]);

  useEffect(() => {
    getMyDocuments()
      .then((data) => setDocs(data.slice(0, 6)))
      .catch(() => {});
  }, []);

  return (
    <div className="bg-white rounded-3xl border shadow-sm p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Recent Activity</h2>
        {docs.length > 0 && (
          <Link
            href="/documents"
            className="text-sm text-blue-600 hover:underline flex items-center gap-1"
          >
            View all <ArrowRight size={14} />
          </Link>
        )}
      </div>

      {docs.length === 0 ? (
        <div className="border rounded-xl p-5">
          <h3 className="font-semibold">No recent activity</h3>
          <p className="text-gray-500 mt-2">Upload your first document to get started.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {docs.map((doc) => {
            const completed = doc.status === "done";
            const Icon = completed ? CheckCircle2 : AlertCircle;

            return (
              <div key={doc.id} className="border rounded-xl p-5 flex items-start gap-4">
                <div className="bg-slate-100 rounded-xl p-3">
                  <FileText className="text-blue-600" size={22} />
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-start justify-between gap-4">
                    <h3 className="font-semibold truncate">{doc.filename}</h3>
                    <span
                      className={`flex items-center gap-1.5 text-xs font-medium shrink-0 ${
                        completed ? "text-green-600" : "text-red-600"
                      }`}
                    >
                      <Icon size={15} />
                      {completed ? "Completed" : "Failed"}
                    </span>
                  </div>

                  <p className="text-gray-500 mt-2 text-sm">
                    {completed
                      ? `${doc.language || "Unknown language"}${
                          doc.pages ? ` · ${doc.pages} page${doc.pages === 1 ? "" : "s"}` : ""
                        }${
                          doc.characters ? ` · ${doc.characters.toLocaleString()} chars` : ""
                        }`
                      : "Processing failed"}
                  </p>

                  <p className="text-xs text-gray-400 mt-2">{formatDate(doc.created_at)}</p>
                </div>

                {completed && (
                  <Link
                    href={`/documents/${doc.id}`}
                    className="shrink-0 text-blue-600 hover:text-blue-700 transition"
                    title="View analysis"
                  >
                    <ArrowRight size={18} />
                  </Link>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
