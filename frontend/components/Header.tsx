import { Globe2 } from "lucide-react";

export default function Header() {
  return (
    <header className="bg-white border-b shadow-sm">
      <div className="max-w-7xl mx-auto flex items-center gap-4 px-8 py-5">
        <div className="bg-blue-600 rounded-xl p-3 text-white">
          <Globe2 size={30} />
        </div>

        <div>
          <h1 className="text-3xl font-bold">
            Polyglot AI Studio
          </h1>

          <p className="text-gray-500">
            AI Powered Multilingual Document Platform
          </p>
        </div>
      </div>
    </header>
  );
}