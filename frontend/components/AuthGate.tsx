"use client";

import { useState, useEffect } from "react";
import { ArrowRight, Eye, EyeOff, FileText, Globe, Layers, Loader2, ShieldCheck } from "lucide-react";
import { loginUser, registerUser } from "@/lib/api";
import { clearAppStorage } from "@/lib/documentActivity";

const FEATURES = [
  {
    icon: FileText,
    title: "Document Intelligence",
    desc: "Upload PDFs, images & docs — get instant AI summaries and translations.",
  },
  {
    icon: Globe,
    title: "15+ Languages",
    desc: "Automatic language detection and bidirectional translation.",
  },
  {
    icon: ShieldCheck,
    title: "Privacy First",
    desc: "AI runs entirely on our servers. Your data never reaches OpenAI or any AI vendor.",
  },
];

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const [checked, setChecked]           = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [authMode, setAuthMode]         = useState<"register" | "login">("register");
  const [name, setName]                 = useState("");
  const [email, setEmail]               = useState("");
  const [password, setPassword]         = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [authError, setAuthError]       = useState("");
  const [submitting, setSubmitting]     = useState(false);

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
    setName("");
    setEmail("");
    setPassword("");
  }

  if (!checked) return null;
  if (authenticated) return <>{children}</>;

  return (
    <div className="min-h-screen flex">

      {/* ── Left panel ── */}
      <div className="hidden lg:flex lg:w-[55%] relative overflow-hidden flex-col justify-between p-14"
           style={{ background: "linear-gradient(135deg, #1d4ed8 0%, #2563eb 40%, #4f46e5 100%)" }}>

        {/* Decorative orbs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none select-none">
          <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-white/5 animate-pulse" />
          <div className="absolute top-1/2 -right-32 w-80 h-80 rounded-full bg-indigo-400/20 animate-pulse"
               style={{ animationDelay: "0.7s" }} />
          <div className="absolute -bottom-32 left-1/3 w-72 h-72 rounded-full bg-blue-300/10 animate-pulse"
               style={{ animationDelay: "1.4s" }} />
          {/* Grid pattern overlay */}
          <div className="absolute inset-0 opacity-5"
               style={{ backgroundImage: "radial-gradient(circle, #fff 1px, transparent 1px)", backgroundSize: "32px 32px" }} />
        </div>

        {/* Top content */}
        <div className="relative z-10">
          <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-1.5 mb-10">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-white/90 text-xs font-medium tracking-wide">AI Running On-Premise</span>
          </div>

          <h1 className="text-5xl font-bold text-white leading-[1.1] tracking-tight">
            Polyglot<br />AI Studio
          </h1>
          <p className="text-blue-200 mt-5 text-lg leading-relaxed max-w-xs">
            Multilingual document intelligence — powered entirely by self-hosted AI.
          </p>
        </div>

        {/* Feature list */}
        <div className="relative z-10 space-y-5">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="flex gap-4 group">
              <div className="shrink-0 w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center
                              group-hover:bg-white/20 transition-colors duration-200">
                <Icon size={18} className="text-white" />
              </div>
              <div>
                <p className="text-white font-semibold text-sm">{title}</p>
                <p className="text-blue-200 text-xs mt-0.5 leading-relaxed">{desc}</p>
              </div>
            </div>
          ))}
        </div>

        <p className="relative z-10 text-blue-300/50 text-xs">
          © 2025 Polyglot AI Studio · No data sent to AI vendors
        </p>
      </div>

      {/* ── Right panel ── */}
      <div className="flex-1 bg-slate-50 flex items-center justify-center p-8">
        <div className="w-full max-w-md">

          {/* Mobile logo */}
          <div className="lg:hidden text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900">Polyglot AI Studio</h1>
            <p className="text-gray-500 text-sm mt-1">Multilingual Document Intelligence</p>
          </div>

          <div className="bg-white rounded-3xl shadow-xl border border-slate-100 p-10">

            {/* Heading */}
            <div className="mb-7">
              <h2 className="text-2xl font-bold text-gray-900">
                {authMode === "register" ? "Create your account" : "Welcome back"}
              </h2>
              <p className="text-gray-400 text-sm mt-1">
                {authMode === "register" ? "Get started — it's free" : "Sign in to continue"}
              </p>
            </div>

            {/* Mode tabs */}
            <div className="flex rounded-xl bg-slate-100 p-1 mb-7">
              {(["register", "login"] as const).map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => switchMode(mode)}
                  className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                    authMode === mode
                      ? "bg-white shadow-sm text-blue-600"
                      : "text-gray-400 hover:text-gray-600"
                  }`}
                >
                  {mode === "register" ? "Sign Up" : "Sign In"}
                </button>
              ))}
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">

              {authMode === "register" && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Full Name</label>
                  <input
                    type="text"
                    required
                    minLength={2}
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Jane Doe"
                    className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm
                               bg-slate-50 focus:bg-white focus:outline-none focus:ring-2
                               focus:ring-blue-500 focus:border-transparent transition-all"
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Email address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm
                             bg-slate-50 focus:bg-white focus:outline-none focus:ring-2
                             focus:ring-blue-500 focus:border-transparent transition-all"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    minLength={8}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Min. 8 characters"
                    className="w-full border border-slate-200 rounded-xl px-4 py-3 pr-11 text-sm
                               bg-slate-50 focus:bg-white focus:outline-none focus:ring-2
                               focus:ring-blue-500 focus:border-transparent transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              {authError && (
                <div className="flex items-start gap-2.5 text-red-600 bg-red-50 border border-red-100
                                rounded-xl px-4 py-3 text-sm">
                  <span className="shrink-0 mt-0.5">⚠</span>
                  <span>{authError}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={submitting}
                className="w-full flex items-center justify-center gap-2 mt-2
                           bg-blue-600 hover:bg-blue-700 disabled:opacity-60
                           text-white rounded-xl py-3.5 font-semibold transition-colors duration-200"
              >
                {submitting
                  ? <Loader2 size={18} className="animate-spin" />
                  : <ArrowRight size={18} />
                }
                {submitting
                  ? authMode === "register" ? "Creating account..." : "Signing in..."
                  : authMode === "register" ? "Create Account" : "Sign In"
                }
              </button>
            </form>

            <p className="text-center text-xs text-gray-400 mt-6 leading-relaxed">
              Your documents are processed on our servers.<br />
              AI never sends data to OpenAI or any external vendor.
            </p>
          </div>
        </div>
      </div>

    </div>
  );
}
