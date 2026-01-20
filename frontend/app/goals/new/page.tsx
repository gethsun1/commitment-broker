"use client";

import { GoalForm } from "@/components/GoalForm";

export default function NewGoalPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <GoalForm />
      </div>
    </div>
  );
}
