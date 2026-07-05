"use client";

import {
    Languages,
    FileText,
    GitCompare,
    Settings,
  } from "lucide-react";
  
  import FeatureCard from "./FeatureCard";
  import QuickStats from "./QuickStats";
  import RecentActivity from "./RecentActivity";
  
  export default function Dashboard() {
    return (
      <div className="space-y-10">
  
        <QuickStats />
  
        <div className="grid md:grid-cols-2 gap-8">
  
          <FeatureCard
            title="Document Intelligence"
            description="Upload multilingual documents, detect language, perform OCR, summarize and chat."
            icon={Languages}
            href="/document-intelligence"
            status="Ready"
          />
  
          <FeatureCard
            title="AI Document Studio"
            description="Write content, translate it and export as PDF or DOCX."
            icon={FileText}
            href="/document-generator"
            status="Ready"
          />
  
          <FeatureCard
            title="Compare Documents"
            description="Compare two or more documents and generate AI insights."
            icon={GitCompare}
            href="/compare"
            status="Coming Soon"
          />
  
          <FeatureCard
            title="Settings"
            description="Configure API keys, model preferences and application settings."
            icon={Settings}
            href="/settings"
            status="Ready"
          />
  
        </div>
  
        <RecentActivity />
  
      </div>
    );
  }