"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, FileText, Loader, CheckCircle, XCircle } from "lucide-react";
import { api } from "@/lib/api";
import { DocumentResponse } from "@/types/documents";

export default function UploadBox() {
  const [result, setResult] = useState<DocumentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (accepted: File[]) => {
    const file = accepted[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const { data } = await api.post<DocumentResponse>("/analyze", formData);
      setResult(data);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Upload failed. Is the backend running?";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: {
      "application/pdf": [".pdf"],
      "image/*": [".png", ".jpg", ".jpeg", ".tiff", ".bmp"],
      "text/plain": [".txt"],
    },
  });

  return (
    <div className="space-y-6">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 bg-white hover:border-blue-400 hover:bg-blue-50"
        }`}
      >
        <input {...getInputProps()} />
        <UploadCloud className="mx-auto mb-4 text-blue-500" size={48} />
        <p className="text-lg font-medium text-gray-700">
          {isDragActive ? "Drop the file here" : "Drag & drop a document, or click to select"}
        </p>
        <p className="mt-1 text-sm text-gray-400">PDF, PNG, JPG, TIFF, TXT</p>
      </div>

      {loading && (
        <div className="flex items-center gap-3 p-4 bg-white rounded-xl shadow-sm">
          <Loader className="animate-spin text-blue-500" size={20} />
          <span className="text-gray-600">Analyzing document…</span>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl">
          <XCircle className="text-red-500 shrink-0" size={20} />
          <span className="text-red-700 text-sm">{error}</span>
        </div>
      )}

      {result && (
        <div className="bg-white rounded-xl shadow-sm divide-y">
          <div className="flex items-center gap-3 p-5">
            <CheckCircle className="text-green-500 shrink-0" size={20} />
            <span className="font-medium text-gray-800">{result.filename}</span>
            <span className="ml-auto text-xs text-gray-400 uppercase">{result.file_type}</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-5 text-sm">
            <Stat label="Language" value={`${result.language} (${result.language_code})`} />
            <Stat label="Pages" value={String(result.pages)} />
            <Stat label="Characters" value={result.characters.toLocaleString()} />
            <Stat label="OCR used" value={result.ocr_used ? "Yes" : "No"} />
          </div>

          {result.preview && (
            <div className="p-5">
              <div className="flex items-center gap-2 mb-2 text-gray-500">
                <FileText size={16} />
                <span className="text-xs font-medium uppercase tracking-wide">Preview</span>
              </div>
              <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed line-clamp-6">
                {result.preview}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-gray-400 text-xs uppercase tracking-wide">{label}</p>
      <p className="font-medium text-gray-800 mt-0.5">{value}</p>
    </div>
  );
}
