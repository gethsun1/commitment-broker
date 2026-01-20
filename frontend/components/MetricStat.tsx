"use client";

import { motion } from "framer-motion";

interface MetricStatProps {
  label: string;
  value: string | number;
  description?: string;
  className?: string;
}

export function MetricStat({
  label,
  value,
  description,
  className,
}: MetricStatProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={className}
    >
      <p className="text-meta-label text-muted-foreground mb-2">{label}</p>
      <p className="text-3xl font-semibold text-foreground mb-1">{value}</p>
      {description && (
        <p className="text-sm text-muted-foreground">{description}</p>
      )}
    </motion.div>
  );
}
