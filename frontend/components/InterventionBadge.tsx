"use client";

import { Intervention } from "@/lib/api";

interface InterventionBadgeProps {
  intervention: Intervention;
  className?: string;
}

const typeConfig = {
  gentle_warning: {
    label: "Warning",
    color: "text-secondary border-secondary/40 bg-secondary/10",
  },
  recommitment_prompt: {
    label: "Recommitment",
    color: "text-primary border-primary/40 bg-primary/10",
  },
  goal_renegotiation: {
    label: "Renegotiation",
    color: "text-destructive border-destructive/40 bg-destructive/10",
  },
};

export function InterventionBadge({
  intervention,
  className,
}: InterventionBadgeProps) {
  const config = typeConfig[intervention.type];

  return (
    <div
      className={`
        inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium
        ${config.color}
        ${className}
      `}
    >
      <span>{config.label}</span>
      {intervention.drift_type && (
        <>
          <span className="opacity-40">•</span>
          <span className="opacity-70 capitalize">{intervention.drift_type}</span>
        </>
      )}
    </div>
  );
}
