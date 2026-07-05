"use client";

import Link from "next/link";
import { LucideIcon, ArrowRight } from "lucide-react";

interface FeatureCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  href: string;
  status: "Ready" | "Coming Soon";
}

export default function FeatureCard({
  title,
  description,
  icon: Icon,
  href,
  status,
}: FeatureCardProps) {
  const ready = status === "Ready";

  return (
    <div className="bg-white rounded-3xl shadow-sm border border-gray-200 hover:shadow-xl transition-all duration-300 p-6 flex flex-col justify-between">

      <div>
        <div className="w-14 h-14 rounded-2xl bg-blue-100 flex items-center justify-center mb-5">
          <Icon className="text-blue-600" size={28} />
        </div>

        <h3 className="text-xl font-bold">
          {title}
        </h3>

        <p className="text-gray-500 mt-3 leading-7">
          {description}
        </p>
      </div>

      <div className="mt-8 flex items-center justify-between">

        <span
          className={`text-sm font-semibold px-3 py-1 rounded-full ${
            ready
              ? "bg-green-100 text-green-700"
              : "bg-yellow-100 text-yellow-700"
          }`}
        >
          {status}
        </span>

        {ready ? (
          <Link href={href}>
            <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl transition">
              Open
              <ArrowRight size={18} />
            </button>
          </Link>
        ) : (
          <button
            disabled
            className="bg-gray-200 px-4 py-2 rounded-xl text-gray-500"
          >
            Soon
          </button>
        )}

      </div>

    </div>
  );
}