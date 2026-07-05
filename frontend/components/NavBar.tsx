"use client";

import { Bell, LogOut, Search, UserCircle2 } from "lucide-react";
import { clearAppStorage } from "@/lib/documentActivity";

export default function Navbar() {
  function handleSignOut() {
    clearAppStorage();
    localStorage.removeItem("access_token");
    window.location.reload();
  }

  return (
    <header className="bg-white border-b h-20 flex items-center justify-between px-8">

      <div>
        <h2 className="text-3xl font-bold">Dashboard</h2>
        <p className="text-gray-500">Welcome to Polyglot AI Studio</p>
      </div>

      <div className="flex items-center gap-6">
        <Search className="cursor-pointer text-gray-500 hover:text-gray-800 transition" />
        <Bell className="cursor-pointer text-gray-500 hover:text-gray-800 transition" />
        <UserCircle2 size={34} className="text-gray-600" />
        <button
          onClick={handleSignOut}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-red-500 transition"
          title="Sign out"
        >
          <LogOut size={20} />
        </button>
      </div>

    </header>
  );
}
