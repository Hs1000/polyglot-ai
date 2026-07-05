"use client";

import {
  Globe2,
  FileText,
  ScanText,
  Type,
} from "lucide-react";

export interface DocumentMetadata {
  language?: string;
  languageCode?: string;
  pages?: number;
  characters?: number;
  ocrUsed?: boolean;
}

interface MetadataCardProps {
  metadata: DocumentMetadata;
}

export default function MetadataCard({
  metadata,
}: MetadataCardProps) {
  const cards = [
    {
      title: "Language",
      value: metadata.language || "--",
      icon: Globe2,
      color: "text-blue-600",
      bg: "bg-blue-100",
    },
    {
      title: "Pages",
      value: metadata.pages ?? "--",
      icon: FileText,
      color: "text-green-600",
      bg: "bg-green-100",
    },
    {
      title: "Characters",
      value: metadata.characters
        ? metadata.characters.toLocaleString()
        : "--",
      icon: Type,
      color: "text-purple-600",
      bg: "bg-purple-100",
    },
    {
      title: "OCR Used",
      value:
        metadata.ocrUsed === undefined
          ? "--"
          : metadata.ocrUsed
          ? "Yes"
          : "No",
      icon: ScanText,
      color: "text-orange-600",
      bg: "bg-orange-100",
    },
  ];

  return (
    <div className="bg-white rounded-3xl border shadow-sm p-6">

      <div className="flex items-center justify-between mb-6">

        <h2 className="text-2xl font-bold">
          Document Metadata
        </h2>

        {metadata.languageCode && (
          <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-medium uppercase">
            {metadata.languageCode}
          </span>
        )}

      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">

        {cards.map((card) => (
          <div
            key={card.title}
            className="border rounded-2xl p-5 hover:shadow-md transition-all"
          >
            <div
              className={`w-12 h-12 rounded-xl flex items-center justify-center ${card.bg}`}
            >
              <card.icon
                className={card.color}
                size={24}
              />
            </div>

            <p className="text-sm text-gray-500 mt-4">
              {card.title}
            </p>

            <h3 className="text-2xl font-bold mt-1">
              {card.value}
            </h3>
          </div>
        ))}

      </div>
    </div>
  );
}