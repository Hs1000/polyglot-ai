"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  FileText,
  FileImage,
  FolderOpen,
  Loader2,
  Trash2,
  ArrowRight,
} from "lucide-react";

import Navbar from "@/components/NavBar";
import Sidebar from "@/components/SideBar";
import { getMyDocuments, deleteDocument, DocumentSummary } from "@/lib/api";

function fileIcon(filename: string) {
  const ext = filename.split(".").pop()?.toLowerCase();
  if (["png", "jpg", "jpeg", "webp"].includes(ext ?? "")) return FileImage;
  return FileText;
}

function statusBadge(status: DocumentSummary["status"]) {
  if (status === "done")
    return (
      <span className="inline-flex items-center gap-1 bg-green-100 text-green-700 text-xs font-semibold px-2.5 py-1 rounded-full">
        Completed
      </span>
    );
  if (status === "processing")
    return (
      <span className="inline-flex items-center gap-1 bg-amber-100 text-amber-700 text-xs font-semibold px-2.5 py-1 rounded-full">
        <Loader2 size={11} className="animate-spin" />
        Processing
      </span>
    );
  return (
    <span className="inline-flex items-center gap-1 bg-red-100 text-red-700 text-xs font-semibold px-2.5 py-1 rounded-full">
      Failed
    </span>
  );
}

function relativeDate(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export default function MyDocumentsPage() {
  const [docs, setDocs] = useState<DocumentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  useEffect(() => {
    getMyDocuments()
      .then(setDocs)
      .catch((err) => {
        if (err.response?.status === 401) {
          localStorage.removeItem("access_token");
          window.location.reload();
          return;
        }
        setError("Failed to load documents.");
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleDelete(id: string) {
    if (confirmDelete !== id) {
      setConfirmDelete(id);
      setTimeout(() => setConfirmDelete((prev) => (prev === id ? null : prev)), 3000);
      return;
    }
    setConfirmDelete(null);
    try {
      await deleteDocument(id);
      setDocs((prev) => prev.filter((d) => d.id !== id));
    } catch {
      setError("Failed to delete document.");
    }
  }

  return (
    <div className="flex bg-slate-100 min-h-screen">
      <Sidebar />
      <div className="flex-1">
        <Navbar />
        <main className="p-8 space-y-6">
          <div>
            <h1 className="text-4xl font-bold">My Documents</h1>
            <p className="text-gray-500 mt-2">Browse and review your previous document analyses.</p>
          </div>

          {loading && (
            <div className="flex items-center justify-center py-32">
              <Loader2 className="animate-spin text-blue-600" size={40} />
            </div>
          )}

          {!loading && error && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-2xl p-6 text-sm">
              {error}
            </div>
          )}

          {!loading && !error && docs.length === 0 && (
            <div className="bg-white border shadow-sm rounded-3xl flex flex-col items-center justify-center py-24 gap-4">
              <FolderOpen className="text-gray-300" size={56} />
              <h2 className="text-xl font-semibold text-gray-600">No documents yet</h2>
              <p className="text-gray-400 text-sm">Upload a file to get started.</p>
              <Link
                href="/document-intelligence"
                className="mt-2 inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-xl font-semibold transition"
              >
                Upload a Document
                <ArrowRight size={18} />
              </Link>
            </div>
          )}

          {!loading && !error && docs.length > 0 && (
            <div className="space-y-3">
              {docs.map((doc) => {
                const Icon = fileIcon(doc.filename);
                const isConfirming = confirmDelete === doc.id;

                return (
                  <div
                    key={doc.id}
                    className="bg-white border shadow-sm rounded-2xl p-5 flex items-center gap-5"
                  >
                    <div className="bg-slate-100 p-3 rounded-xl shrink-0">
                      <Icon size={24} className="text-slate-500" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 flex-wrap">
                        <p className="font-semibold text-gray-900 truncate">{doc.filename}</p>
                        {statusBadge(doc.status)}
                        {doc.language && (
                          <span className="bg-slate-100 text-slate-600 text-xs font-medium px-2 py-0.5 rounded-full uppercase">
                            {doc.language}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-4 mt-1 text-xs text-gray-400">
                        {doc.pages != null && <span>{doc.pages} pages</span>}
                        {doc.characters != null && (
                          <span>{doc.characters.toLocaleString()} chars</span>
                        )}
                        <span>{relativeDate(doc.created_at)}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      {doc.status === "done" && (
                        <Link
                          href={`/documents/${doc.id}`}
                          className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2 rounded-xl transition"
                        >
                          View Analysis
                          <ArrowRight size={15} />
                        </Link>
                      )}

                      <button
                        onClick={() => handleDelete(doc.id)}
                        className={`inline-flex items-center gap-1.5 text-sm font-semibold px-3 py-2 rounded-xl transition ${
                          isConfirming
                            ? "bg-red-600 text-white"
                            : "bg-slate-100 hover:bg-red-50 text-slate-500 hover:text-red-600"
                        }`}
                      >
                        {isConfirming ? (
                          "Confirm?"
                        ) : (
                          <Trash2 size={16} />
                        )}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
