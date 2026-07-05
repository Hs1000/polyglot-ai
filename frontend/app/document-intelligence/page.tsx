import Sidebar from "@/components/SideBar";
import Navbar from "@/components/NavBar";

import DocumentWorkspace from "@/components/document/DocumentWorkspace";

export default function DocumentIntelligencePage() {
  return (
    <div className="flex bg-slate-100 min-h-screen">

      <Sidebar />

      <div className="flex-1">

        <Navbar />

        <main className="p-8">

          <div className="mb-8">

            <h1 className="text-4xl font-bold">
              Document Intelligence
            </h1>

            <p className="text-gray-500 mt-2">
              Upload multilingual documents and let AI understand them.
            </p>

          </div>

          <DocumentWorkspace />

        </main>

      </div>

    </div>
  );
}