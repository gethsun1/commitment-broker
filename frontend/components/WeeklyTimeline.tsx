"use client";

import { motion } from "framer-motion";

interface WeeklyTimelineProps {
  weeks: number;
  compliantWeeks: number[];
  className?: string;
}

export function WeeklyTimeline({
  weeks,
  compliantWeeks,
  className,
}: WeeklyTimelineProps) {
  return (
    <div className={className}>
      <div className="flex items-center gap-2 flex-wrap">
        {Array.from({ length: weeks }, (_, i) => {
          const weekNum = i + 1;
          const isCompliant = compliantWeeks.includes(weekNum);
          return (
            <motion.div
              key={weekNum}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
              className={`
                w-10 h-10 rounded-lg border-2 flex items-center justify-center text-xs font-medium
                transition-colors
                ${
                  isCompliant
                    ? "bg-primary/20 border-primary/40 text-primary"
                    : "bg-muted/20 border-muted/40 text-muted-foreground"
                }
              `}
              title={`Week ${weekNum}: ${isCompliant ? "Compliant" : "Pending"}`}
            >
              {weekNum}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
