"use client";

import { UploadCloud } from "lucide-react";

interface UploadCardProps {
  onBrowse: () => void;
}

export default function UploadCard({
  onBrowse,
}: UploadCardProps) {
  return (
    <div className="bg-white rounded-3xl border border-dashed border-blue-300 p-12 shadow-sm hover:shadow-lg transition">

      <div className="flex flex-col items-center text-center">

        <div className="bg-blue-100 rounded-full p-6 mb-6">

          <UploadCloud
            size={45}
            className="text-blue-600"
          />

        </div>

        <h2 className="text-2xl font-bold">
          Upload Document
        </h2>

        <p className="text-gray-500 mt-3">
          Drag & Drop your document here
        </p>

        <span className="my-4 text-gray-400">
          OR
        </span>

        <button
          onClick={onBrowse}
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl px-6 py-3 font-semibold transition"
        >
          Browse Files
        </button>

        <p className="text-gray-400 mt-8 text-sm">
          Supported formats:
          PDF • DOCX • TXT • PNG • JPG
        </p>

      </div>

    </div>
  );
}