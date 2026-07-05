"use client";

import Link from "next/link";
import {
  LayoutDashboard,
  Languages,
  FileText,
  FolderOpen,
  GitCompare,
  Settings,
  Globe2,
} from "lucide-react";

import { usePathname } from "next/navigation";

const menu = [
  {
    title: "Dashboard",
    icon: LayoutDashboard,
    href: "/",
  },
  {
    title: "Document Intelligence",
    icon: Languages,
    href: "/document-intelligence",
  },
  {
    title: "My Documents",
    icon: FolderOpen,
    href: "/documents",
  },
  {
    title: "AI Document Studio",
    icon: FileText,
    href: "/document-generator",
  },
  {
    title: "Compare Documents",
    icon: GitCompare,
    href: "/compare",
  },
  {
    title: "Settings",
    icon: Settings,
    href: "/settings",
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-72 h-screen bg-white border-r flex flex-col">

      <div className="flex items-center gap-3 p-6 border-b">

        <div className="bg-blue-600 p-3 rounded-xl text-white">
          <Globe2 size={28} />
        </div>

        <div>
          <h1 className="font-bold text-xl">
            Polyglot AI
          </h1>

          <p className="text-sm text-gray-500">
            Studio
          </p>
        </div>

      </div>

      <nav className="flex-1 p-5 space-y-2">

        {menu.map((item) => {

          const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);

          return (
            <Link
              key={item.title}
              href={item.href}
              className={`flex items-center gap-4 rounded-xl p-4 transition

              ${
                active
                  ? "bg-blue-600 text-white"
                  : "hover:bg-slate-100"
              }
              `}
            >
              <item.icon size={22} />

              {item.title}
            </Link>
          );
        })}

      </nav>

    </aside>
  );
}