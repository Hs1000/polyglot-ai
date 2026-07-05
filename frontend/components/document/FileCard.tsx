"use client";

import {
  FileText,
  FileImage,
  FileSpreadsheet,
  FileCode2,
  File,
  CheckCircle2,
  Loader2,
  AlertCircle,
  Trash2,
} from "lucide-react";

export type UploadStatus =
  | "ready"
  | "uploading"
  | "processing"
  | "completed"
  | "error";

interface FileCardProps {
  file: {
    name: string;
    size: number;
  };
  status?: UploadStatus;
  progress?: number;
  message?: string;
  onRemove: () => void;
}

export default function FileCard({
  file,
  status = "ready",
  progress = 0,
  message,
  onRemove,
}: FileCardProps) {
  const extension = file.name.split(".").pop()?.toLowerCase();

  const size = (file.size / 1024 / 1024).toFixed(2);

  function getIcon() {
    switch (extension) {
      case "pdf":
        return <FileText className="text-red-500" size={42} />;

      case "docx":
      case "doc":
        return <FileText className="text-blue-500" size={42} />;

      case "txt":
      case "md":
        return <FileCode2 className="text-gray-600" size={42} />;

      case "csv":
      case "xlsx":
        return (
          <FileSpreadsheet
            className="text-green-600"
            size={42}
          />
        );

      case "png":
      case "jpg":
      case "jpeg":
        return (
          <FileImage
            className="text-purple-500"
            size={42}
          />
        );

      default:
        return <File size={42} />;
    }
  }

  function getBadge() {
    switch (status) {
      case "ready":
        return (
          <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full">
            Ready
          </span>
        );

      case "uploading":
        return (
          <span className="flex items-center gap-2 bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full">
            <Loader2
              className="animate-spin"
              size={16}
            />
            Uploading
          </span>
        );

      case "processing":
        return (
          <span className="flex items-center gap-2 bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full">
            <Loader2
              className="animate-spin"
              size={16}
            />
            Processing
          </span>
        );

      case "completed":
        return (
          <span className="flex items-center gap-2 bg-green-100 text-green-700 px-3 py-1 rounded-full">
            <CheckCircle2 size={16} />
            Completed
          </span>
        );

      case "error":
        return (
          <span className="flex items-center gap-2 bg-red-100 text-red-700 px-3 py-1 rounded-full">
            <AlertCircle size={16} />
            Failed
          </span>
        );
    }
  }

  return (
    <div className="bg-white rounded-3xl border border-gray-200 shadow-sm hover:shadow-lg transition-all">

      <div className="p-6 flex justify-between">

        <div className="flex gap-5">

          <div>{getIcon()}</div>

          <div>

            <h2 className="font-bold text-lg">
              {file.name}
            </h2>

            <p className="text-gray-500">
              {extension?.toUpperCase()} • {size} MB
            </p>

            {message && (
              <p className="text-sm text-gray-400 mt-2">
                {message}
              </p>
            )}

          </div>

        </div>

        <button
          onClick={onRemove}
          className="text-gray-400 hover:text-red-500 transition"
        >
          <Trash2 />
        </button>

      </div>

      {(status === "uploading" ||
        status === "processing") && (
        <div className="px-6 pb-4">

          <div className="w-full bg-gray-200 rounded-full h-2">

            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{
                width: `${progress}%`,
              }}
            />

          </div>

          <p className="text-xs text-gray-500 mt-2">
            {progress}% completed
          </p>

        </div>
      )}

      <div className="px-6 py-4 border-t flex justify-between items-center">

        <span className="text-gray-500">
          Status
        </span>

        {getBadge()}

      </div>

    </div>
  );
}
