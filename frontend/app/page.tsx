import Sidebar from "@/components/SideBar";
import Navbar from "@/components/NavBar";
import Dashboard from "@/components/Dashboard";

export default function Home() {
  return (
    <div className="flex bg-slate-100 min-h-screen">

      <Sidebar />

      <div className="flex-1">

        <Navbar />

        <main className="p-8">
          <Dashboard />
        </main>

      </div>

    </div>
  );
}