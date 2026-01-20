"use client";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Intervention } from "@/lib/api";
import { AlertCircle, Info, AlertTriangle } from "lucide-react";
import { format } from "date-fns";

interface InterventionAlertProps {
  intervention: Intervention;
  onOutcomeUpdate?: (interventionId: number, outcome: string) => void;
}

export function InterventionAlert({
  intervention,
  onOutcomeUpdate,
}: InterventionAlertProps) {
  const getVariant = () => {
    switch (intervention.type) {
      case "gentle_warning":
        return "warning";
      case "recommitment_prompt":
        return "default";
      case "goal_renegotiation":
        return "destructive";
      default:
        return "default";
    }
  };

  const getIcon = () => {
    switch (intervention.type) {
      case "gentle_warning":
        return <Info className="h-4 w-4" />;
      case "recommitment_prompt":
        return <AlertCircle className="h-4 w-4" />;
      case "goal_renegotiation":
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  const getTitle = () => {
    switch (intervention.type) {
      case "gentle_warning":
        return "Gentle Reminder";
      case "recommitment_prompt":
        return "Recommitment Needed";
      case "goal_renegotiation":
        return "Goal Adjustment Suggested";
      default:
        return "Intervention";
    }
  };

  const handleOutcome = (outcome: string) => {
    if (onOutcomeUpdate) {
      onOutcomeUpdate(intervention.id, outcome);
    }
  };

  return (
    <Alert variant={getVariant()}>
      <div className="flex items-start gap-3">
        {getIcon()}
        <div className="flex-1 space-y-2">
          <AlertTitle>{getTitle()}</AlertTitle>
          <AlertDescription className="whitespace-pre-wrap">
            {intervention.message}
          </AlertDescription>
          <div className="text-xs text-muted-foreground mt-2">
            {format(new Date(intervention.triggered_at), "MMM d, yyyy 'at' h:mm a")}
            {intervention.drift_type && ` • Drift: ${intervention.drift_type}`}
          </div>
          {!intervention.outcome && onOutcomeUpdate && (
            <div className="flex gap-2 mt-4">
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleOutcome("success")}
              >
                Mark as Successful
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleOutcome("ignored")}
              >
                Mark as Ignored
              </Button>
            </div>
          )}
          {intervention.outcome && (
            <div className="text-xs text-muted-foreground mt-2">
              Outcome: <span className="font-medium">{intervention.outcome}</span>
            </div>
          )}
        </div>
      </div>
    </Alert>
  );
}
