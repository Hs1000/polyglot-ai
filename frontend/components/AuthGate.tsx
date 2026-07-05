"use client";

import { useState, useEffect } from "react";
import { loginUser, registerUser } from "@/lib/api";
import { clearAppStorage } from "@/lib/documentActivity";

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const [checked, setChecked] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);

  const [authMode, setAuthMode] = useState<"register" | "login">("register");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    setAuthenticated(!!token);
    setChecked(true);
  }, []);

  async function handleSubmit(e: React.SyntheticEvent<HTMLFormElement>) {
    e.preventDefault();
    setSubmitting(true);
    setAuthError("");
    try {
      if (authMode === "register") {
        await registerUser(name, email, password);
      } else {
        await loginUser(email, password);
      }
      clearAppStorage();
      setAuthenticated(true);
    } catch (err: any) {
      setAuthError(err.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  function switchMode(mode: "register" | "login") {
    setAuthMode(mode);
    setAuthError("");
  }

  if (!checked) return null;

  if (authenticated) return <>{children}</>;

  return (
    <div className="min-h-screen bg-slate-100 flex">

      {/* Left Panel — Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-blue-600 flex-col justify-between p-12">
        <div>
          <h1 className="text-white text-3xl font-bold tracking-tight">
            Polyglot AI Studio
          </h1>
          <p className="text-blue-200 mt-2 text-sm">
            Multilingual Document Intelligence
          </p>
        </div>

        <div className="space-y-8">
          {[
            { title: "Document Intelligence", desc: "Upload PDFs and DOCX files — AI extracts, translates, and summarizes them instantly." },
            { title: "Multilingual Support", desc: "Process documents in 15+ languages with automatic detection and translation." },
            { title: "OCR Included", desc: "Scanned documents? No problem. Built-in OCR extracts text from images." },
          ].map((f) => (
            <div key={f.title} className="flex gap-4">
              <div className="w-1 rounded-full bg-blue-400 shrink-0" />
              <div>
                <h3 className="text-white font-semibold">{f.title}</h3>
                <p className="text-blue-200 text-sm mt-1">{f.desc}</p>
              </div>
            </div>
          ))}
        </div>

        <p className="text-blue-300 text-xs">
          © 2025 Polyglot AI Studio
        </p>
      </div>

      {/* Right Panel — Auth Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="bg-white rounded-3xl shadow-xl border w-full max-w-md p-10">

          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900">
              {authMode === "register" ? "Create your profile" : "Welcome back"}
            </h2>
            <p className="text-gray-500 text-sm mt-1">
              {authMode === "register"
                ? "Set up your account to get started"
                : "Sign in to continue to Polyglot AI Studio"}
            </p>
          </div>

          {/* Tabs */}
          <div className="flex rounded-xl bg-slate-100 p-1 mb-8">
            <button
              type="button"
              onClick={() => switchMode("register")}
              className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition ${
                authMode === "register"
                  ? "bg-white shadow text-blue-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              Create Profile
            </button>
            <button
              type="button"
              onClick={() => switchMode("login")}
              className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition ${
                authMode === "login"
                  ? "bg-white shadow text-blue-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              Sign In
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {authMode === "register" && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Full Name
                </label>
                <input
                  type="text"
                  required
                  minLength={2}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Jane Doe"
                  className="w-full border rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Email
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full border rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Password
              </label>
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Min. 8 characters"
                className="w-full border rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {authError && (
              <p className="text-red-500 text-sm bg-red-50 border border-red-100 rounded-xl px-4 py-3">
                {authError}
              </p>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white rounded-xl py-3 font-semibold transition"
            >
              {submitting
                ? authMode === "register" ? "Creating profile..." : "Signing in..."
                : authMode === "register" ? "Create Profile" : "Sign In"}
            </button>
          </form>

        </div>
      </div>

    </div>
  );
}
