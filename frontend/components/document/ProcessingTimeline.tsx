"use client";

import {
  CheckCircle2,
  Circle,
  Loader2,
} from "lucide-react";

export type ProcessingStep =
  | "upload"
  | "ocr"
  | "language"
  | "translation"
  | "summary"
  | "completed";

interface ProcessingTimelineProps {
  currentStep?: ProcessingStep;
}

const steps = [
  {
    id: "upload",
    title: "Upload Document",
    description: "Uploading your document",
  },
  {
    id: "ocr",
    title: "OCR",
    description: "Extracting text from scanned pages",
  },
  {
    id: "language",
    title: "Language Detection",
    description: "Identifying document language",
  },
  {
    id: "translation",
    title: "Translation",
    description: "Translating if required",
  },
  {
    id: "summary",
    title: "Summarization",
    description: "Generating document summary",
  },
] as const;

export default function ProcessingTimeline({
  currentStep = "upload",
}: ProcessingTimelineProps) {

  const currentIndex =
    currentStep === "completed"
      ? steps.length
      : steps.findIndex(
          (step) => step.id === currentStep
        );

  return (
    <div className="bg-white rounded-3xl border shadow-sm p-6">

      <h2 className="text-xl font-bold mb-6">
        Processing Pipeline
      </h2>

      <div className="space-y-5">

        {steps.map((step, index) => {

          const completed = index < currentIndex;

          const active = index === currentIndex;

          return (
            <div
              key={step.id}
              className="flex items-start gap-4"
            >
              <div className="mt-1">

                {completed ? (
                  <CheckCircle2
                    className="text-green-500"
                    size={22}
                  />
                ) : active ? (
                  <Loader2
                    className="text-blue-600 animate-spin"
                    size={22}
                  />
                ) : (
                  <Circle
                    className="text-gray-300"
                    size={22}
                  />
                )}

              </div>

              <div>

                <h3
                  className={`font-semibold ${
                    completed
                      ? "text-green-600"
                      : active
                      ? "text-blue-600"
                      : "text-gray-400"
                  }`}
                >
                  {step.title}
                </h3>

                <p className="text-sm text-gray-500 mt-1">
                  {step.description}
                </p>

              </div>

            </div>
          );
        })}

      </div>

    </div>
  );
}