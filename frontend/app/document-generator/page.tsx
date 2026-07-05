"use client";

import { useState } from "react";
import { ArrowLeftRight, Copy, Download, Languages, Loader2, Wand2 } from "lucide-react";

import Navbar from "@/components/NavBar";
import Sidebar from "@/components/SideBar";
import { exportTextPdf, translateText } from "@/lib/api";

const LANGUAGES = [
  { code: "es", label: "Spanish" },
  { code: "fr", label: "French" },
  { code: "de", label: "German" },
  { code: "it", label: "Italian" },
  { code: "pt", label: "Portuguese" },
  { code: "ru", label: "Russian" },
  { code: "zh", label: "Chinese" },
  { code: "ja", label: "Japanese" },
  { code: "ko", label: "Korean" },
  { code: "ar", label: "Arabic" },
  { code: "nl", label: "Dutch" },
  { code: "pl", label: "Polish" },
  { code: "tr", label: "Turkish" },
  { code: "sv", label: "Swedish" },
  { code: "uk", label: "Ukrainian" },
];

export default function DocumentGenerator() {
  const [selectedLang, setSelectedLang] = useState("fr");
  const [toEnglish, setToEnglish] = useState(true); // true = other→en, false = en→other
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("");
  const [message, setMessage] = useState("");
  const [isTranslating, setIsTranslating] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  const selectedLabel = LANGUAGES.find((l) => l.code === selectedLang)?.label ?? selectedLang;
  const leftLabel = toEnglish ? selectedLabel : "English";
  const rightLabel = toEnglish ? "English" : selectedLabel;

  function handleSwap() {
    setToEnglish((prev) => !prev);
    setInput(output);
    setOutput("");
    setMessage("");
  }

  async function handleTranslate() {
    const text = input.trim();
    if (!text) {
      setMessage("Enter text to translate.");
      return;
    }

    setIsTranslating(true);
    setMessage("");

    const sourceLang = toEnglish ? selectedLang : "en";
    const targetLang = toEnglish ? "en" : selectedLang;

    try {
      const result = await translateText(text, sourceLang, targetLang);
      setOutput(result.translated_text);
      setMessage(
        result.translation_available
          ? `Translated to ${rightLabel}`
          : "No model available for that language yet — original text returned.",
      );
    } catch (err: any) {
      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        window.location.reload();
        return;
      }
      setMessage(err.response?.data?.detail || "Translation failed.");
    } finally {
      setIsTranslating(false);
    }
  }

  async function copyOutput() {
    if (!output) return;
    await navigator.clipboard.writeText(output);
  }

  async function handleDownloadPdf() {
    if (!output || isDownloading) return;
    setIsDownloading(true);
    try {
      await exportTextPdf(
        output,
        `translation_${rightLabel.toLowerCase()}`,
        `${leftLabel} → ${rightLabel}`,
      );
    } catch (err: any) {
      if (err?.response?.status === 401) {
        localStorage.removeItem("access_token");
        window.location.reload();
      }
    } finally {
      setIsDownloading(false);
    }
  }

  return (
    <div className="flex bg-slate-100 min-h-screen">
      <Sidebar />

      <div className="flex-1">
        <Navbar />

        <main className="p-8 space-y-8">
          <div>
            <h1 className="text-4xl font-bold">AI Document Studio</h1>
            <p className="text-gray-500 mt-2">
              Translate multilingual content in both directions.
            </p>
          </div>

          <section className="bg-white border shadow-sm rounded-3xl">
            {/* Header */}
            <div className="border-b p-6 flex items-center justify-between gap-4 flex-wrap">
              <div className="flex items-center gap-3">
                <div className="bg-blue-100 text-blue-600 rounded-xl p-3">
                  <Languages size={24} />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">Translator</h2>
                  <p className="text-sm text-gray-500">Bidirectional translation</p>
                </div>
              </div>

              {/* Direction controls */}
              <div className="flex items-center gap-3">
                <span className="text-sm font-semibold text-gray-700 min-w-[80px] text-right">
                  {leftLabel}
                </span>

                <button
                  onClick={handleSwap}
                  title="Swap direction"
                  className="p-2 rounded-xl border bg-white hover:bg-slate-50 transition"
                >
                  <ArrowLeftRight size={18} className="text-blue-600" />
                </button>

                <span className="text-sm font-semibold text-gray-700 min-w-[80px]">
                  {rightLabel}
                </span>

                <select
                  value={selectedLang}
                  onChange={(e) => {
                    setSelectedLang(e.target.value);
                    setOutput("");
                    setMessage("");
                  }}
                  className="border rounded-xl px-4 py-3 bg-white text-sm font-medium"
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Panels */}
            <div className="grid lg:grid-cols-2 gap-0">
              <div className="p-6 border-b lg:border-b-0 lg:border-r">
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-3">
                  {leftLabel}
                </p>
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={`Type in ${leftLabel}…`}
                  className="w-full min-h-96 resize-none outline-none text-base leading-7"
                />
              </div>

              <div className="p-6 bg-slate-50 rounded-b-3xl lg:rounded-bl-none lg:rounded-r-3xl">
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-3">
                  {rightLabel}
                </p>
                {output ? (
                  <div className="whitespace-pre-wrap text-base leading-7 text-gray-800">
                    {output}
                  </div>
                ) : (
                  <div className="min-h-96 flex items-center justify-center text-center text-gray-400">
                    <div>
                      <Wand2 className="mx-auto mb-4" size={44} />
                      <p className="font-semibold">Translation will appear here</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="p-6 border-t flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <p className="text-sm text-gray-500">{message}</p>

              <div className="flex gap-3">
                <button
                  onClick={copyOutput}
                  disabled={!output}
                  className="inline-flex items-center gap-2 bg-slate-100 hover:bg-slate-200 disabled:opacity-50 px-4 py-3 rounded-xl font-semibold transition"
                >
                  <Copy size={18} />
                  Copy
                </button>

                <button
                  onClick={handleDownloadPdf}
                  disabled={!output || isDownloading}
                  className="inline-flex items-center gap-2 bg-slate-100 hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed px-4 py-3 rounded-xl font-semibold transition"
                >
                  {isDownloading
                    ? <Loader2 className="animate-spin" size={18} />
                    : <Download size={18} />
                  }
                  Download PDF
                </button>

                <button
                  onClick={handleTranslate}
                  disabled={isTranslating}
                  className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-5 py-3 rounded-xl font-semibold transition"
                >
                  {isTranslating ? (
                    <Loader2 className="animate-spin" size={18} />
                  ) : (
                    <Languages size={18} />
                  )}
                  Translate
                </button>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
