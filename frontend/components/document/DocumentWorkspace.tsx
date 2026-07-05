"use client";

import { useEffect, useRef, useState } from "react";

import UploadCard from "./UploadCard";
import FileCard, { UploadStatus } from "./FileCard";
import ProcessingTimeline, { ProcessingStep } from "./ProcessingTimeline";
import MetadataCard, { DocumentMetadata } from "./MetadataCard";
import PreviewCard from "./PreviewCard";
import AssistantPanel from "./AssistantPanel";
import ExtractionCard from "./ExtractionCard";
import MatchingPanel from "./MatchingPanel";
import { uploadFile, getDocumentStatus } from "@/lib/api";
import {
  clearCurrentDocument,
  getCurrentDocument,
  saveCurrentDocument,
} from "@/lib/documentActivity";

const LANGUAGE_NAMES: Record<string, string> = {
  en: "English", fr: "French", de: "German", es: "Spanish",
  it: "Italian", pt: "Portuguese", ru: "Russian", zh: "Chinese",
  ja: "Japanese", ko: "Korean", ar: "Arabic", nl: "Dutch",
  pl: "Polish", tr: "Turkish", sv: "Swedish", uk: "Ukrainian",
};

const STEPS: ProcessingStep[] = ["upload", "ocr", "language", "translation", "summary"];

type WorkspaceFile = File | {
  name: string;
  size: number;
};

interface DocumentState {
  file: WorkspaceFile | null;
  documentId: string;
  status: UploadStatus;
  currentStep: ProcessingStep;
  progress: number;
  metadata: DocumentMetadata;
  summary: string;
  preview: string;
  translatedText: string;
  message: string;
}

const initialState: DocumentState = {
  file: null,
  documentId: "",
  status: "ready",
  currentStep: "upload",
  progress: 0,
  metadata: {},
  summary: "",
  preview: "",
  translatedText: "",
  message: "",
};

export default function DocumentWorkspace() {
  const [doc, setDoc] = useState<DocumentState>(initialState);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const stepTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const progressTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const current = getCurrentDocument();

    if (current) {
      setDoc({
        file: {
          name: current.filename,
          size: current.fileSize || 0,
        },
        documentId: current.id || "",
        status: current.status === "completed" ? "completed" : "error",
        currentStep: current.status === "completed" ? "completed" : "upload",
        progress: current.status === "completed" ? 100 : 0,
        metadata: {
          language: current.language || "",
          languageCode: current.languageCode || "",
          pages: current.pages ?? undefined,
          characters: current.characters ?? undefined,
          ocrUsed: current.ocrUsed ?? undefined,
        },
        summary: current.summary || "",
        preview: current.preview || "",
        translatedText: current.translatedText || "",
        message:
          current.status === "completed"
            ? "Restored from your last upload"
            : "Last processing attempt failed",
      });
    }

    return () => {
      clearInterval(stepTimerRef.current!);
      clearInterval(progressTimerRef.current!);
      clearInterval(pollTimerRef.current!);
    };
  }, []);

  function browseFiles() {
    fileInputRef.current?.click();
  }

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    clearCurrentDocument();
    setDoc({ ...initialState, file, status: "ready", message: "Ready to upload" });
  }

  function removeFile() {
    clearInterval(stepTimerRef.current!);
    clearInterval(progressTimerRef.current!);
    clearInterval(pollTimerRef.current!);
    clearCurrentDocument();
    setDoc(initialState);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  function isUploadableFile(file: WorkspaceFile | null): file is File {
    return typeof File !== "undefined" && file instanceof File;
  }

  async function handleUpload() {
    if (!isUploadableFile(doc.file)) return;

    const file = doc.file;

    clearInterval(stepTimerRef.current!);
    clearInterval(progressTimerRef.current!);
    clearInterval(pollTimerRef.current!);

    setDoc((prev) => ({
      ...prev,
      status: "uploading",
      currentStep: "upload",
      progress: 0,
      message: "Uploading...",
    }));

    try {
      const { document_id } = await uploadFile(file);
      setDoc((prev) => ({ ...prev, documentId: document_id }));

      let stepIdx = 0;
      stepTimerRef.current = setInterval(() => {
        stepIdx = Math.min(stepIdx + 1, STEPS.length - 1);
        setDoc((prev) => ({ ...prev, currentStep: STEPS[stepIdx], status: "processing" }));
      }, 1500);

      let pct = 0;
      progressTimerRef.current = setInterval(() => {
        pct = Math.min(pct + 2, 90);
        setDoc((prev) => ({ ...prev, progress: pct }));
      }, 400);

      pollTimerRef.current = setInterval(async () => {
        try {
          const result = await getDocumentStatus(document_id);

          if (result.status === "done") {
            clearInterval(stepTimerRef.current!);
            clearInterval(progressTimerRef.current!);
            clearInterval(pollTimerRef.current!);

            const language = LANGUAGE_NAMES[result.language] || result.language || "--";

            const currentDocument = {
              id: document_id,
              filename: file.name,
              fileSize: file.size,
              status: "completed",
              language,
              languageCode: result.language,
              pages: result.pages,
              characters: result.characters,
              ocrUsed: result.ocr_used,
              summary: result.summary || "",
              preview: result.extracted_text || "",
              translatedText: result.translated_text || "",
              createdAt: new Date().toISOString(),
            } as const;

            saveCurrentDocument(currentDocument);

            setDoc((prev) => ({
              ...prev,
              status: "completed",
              currentStep: "completed",
              progress: 100,
              message: "Processing complete",
              metadata: {
                language,
                languageCode: result.language,
                pages: result.pages,
                characters: result.characters,
                ocrUsed: result.ocr_used,
              },
              summary: result.summary || "",
              preview: result.extracted_text || "",
              translatedText: result.translated_text || "",
            }));
          } else if (result.status === "failed") {
            clearInterval(stepTimerRef.current!);
            clearInterval(progressTimerRef.current!);
            clearInterval(pollTimerRef.current!);

            const currentDocument = {
              id: document_id,
              filename: file.name,
              fileSize: file.size,
              status: "failed",
              createdAt: new Date().toISOString(),
            } as const;

            saveCurrentDocument(currentDocument);

            setDoc((prev) => ({
              ...prev,
              status: "error",
              message: result.error || "Processing failed",
              progress: 0,
            }));
          }
        } catch {
          // ignore transient poll errors
        }
      }, 2000);

    } catch (err: any) {
      clearInterval(stepTimerRef.current!);
      clearInterval(progressTimerRef.current!);
      clearInterval(pollTimerRef.current!);

      if (err.response?.status === 401) {
        // Token expired — clear and reload to show the auth screen
        localStorage.removeItem("access_token");
        window.location.reload();
      } else {
        setDoc((prev) => ({
          ...prev,
          status: "error",
          message: err.response?.data?.detail || "Upload failed",
        }));
      }
    }
  }

  return (
    <>
      <input
        ref={fileInputRef}
        hidden
        type="file"
        accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
        onChange={handleFileSelect}
      />

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">

        <div className="xl:col-span-3 space-y-6">
          {!doc.file ? (
            <UploadCard onBrowse={browseFiles} />
          ) : (
            <>
              <FileCard
                file={doc.file}
                status={doc.status}
                progress={doc.progress}
                message={doc.message}
                onRemove={removeFile}
              />

              <div className="flex justify-end">
                <button
                  onClick={handleUpload}
                  disabled={
                    !isUploadableFile(doc.file) ||
                    doc.status === "uploading" ||
                    doc.status === "processing"
                  }
                  className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-6 py-3 rounded-xl font-semibold transition"
                >
                  {doc.status === "completed" ? "Uploaded" : "Upload Document"}
                </button>
              </div>

              <ProcessingTimeline currentStep={doc.currentStep} />
              <MetadataCard metadata={doc.metadata} />
              <PreviewCard
                documentId={doc.documentId}
                filename={doc.file?.name}
                summary={doc.summary}
                preview={doc.preview}
                translatedText={doc.translatedText}
              />
            </>
          )}
        </div>

        <div className="space-y-6">
          <ExtractionCard
            documentId={doc.documentId}
            hasText={doc.status === "completed" && !!doc.preview}
          />
          <AssistantPanel
            documentId={doc.documentId}
            hasText={doc.status === "completed" && !!doc.preview}
          />
          <MatchingPanel
            documentId={doc.documentId}
            hasText={doc.status === "completed" && !!doc.preview}
          />
        </div>

      </div>
    </>
  );
}
