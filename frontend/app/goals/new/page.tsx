"use client";

import { motion } from "framer-motion";
import { GoalForm } from "@/components/GoalForm";

export default function NewGoalPage() {
  return (
    <div className="min-h-screen bg-background py-12">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-4xl mx-auto"
        >
          <GoalForm />
        </motion.div>
      </div>
    </div>
  );
}
