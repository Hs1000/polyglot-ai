"use client";

import { useEffect, useState } from "react";
import { FileText, Languages, FileOutput } from "lucide-react";

import { getMyDocuments, DocumentSummary } from "@/lib/api";

export default function QuickStats() {
  const [docs, setDocs] = useState<DocumentSummary[]>([]);

  useEffect(() => {
    getMyDocuments()
      .then((data) => setDocs(data.filter((d) => d.status === "done")))
      .catch(() => {});
  }, []);

  const languages = new Set(docs.map((d) => d.language).filter(Boolean));
  const withSummary = docs.filter((d) => d.summary).length;

  const stats = [
    { title: "Documents", value: docs.length, icon: FileText },
    { title: "Languages", value: languages.size, icon: Languages },
    { title: "Generated Files", value: withSummary, icon: FileOutput },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {stats.map((stat) => (
        <div key={stat.title} className="bg-white rounded-2xl border p-6 shadow-sm">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-500">{stat.title}</p>
              <h2 className="text-4xl font-bold mt-2">{stat.value}</h2>
            </div>
            <stat.icon className="text-blue-600" size={34} />
          </div>
        </div>
      ))}
    </div>
  );
}
