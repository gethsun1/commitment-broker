"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { CommitmentCard } from "@/components/CommitmentCard";
import { SpendingTracker } from "@/components/SpendingTracker";
import { InterventionAlert } from "@/components/InterventionAlert";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricStat } from "@/components/MetricStat";
import { InterventionBadge } from "@/components/InterventionBadge";
import { apiClient, Commitment, Spending, Intervention, Evaluation, Drift } from "@/lib/api";

export default function CommitmentPage() {
  const params = useParams();
  const router = useRouter();
  const commitmentId = parseInt(params.id as string);

  const [commitment, setCommitment] = useState<Commitment | null>(null);
  const [spendingLogs, setSpendingLogs] = useState<Spending[]>([]);
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [drift, setDrift] = useState<Drift | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [commitmentData, spendingData, interventionsData, evaluationData, driftData] =
        await Promise.all([
          apiClient.commitments.get(commitmentId),
          apiClient.commitments.getSpending(commitmentId),
          apiClient.commitments.getInterventions(commitmentId),
          apiClient.commitments.getEvaluation(commitmentId).catch(() => null),
          apiClient.commitments.getDrift(commitmentId).catch(() => null),
        ]);

      setCommitment(commitmentData);
      setSpendingLogs(spendingData);
      setInterventions(interventionsData);
      setEvaluation(evaluationData);
      setDrift(driftData);
    } catch (error) {
      console.error("Error loading data:", error);
      alert("Failed to load commitment data.");
    } finally {
      setLoading(false);
    }
  }, [commitmentId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSpendingAdded = () => {
    loadData();
  };

  const handleOutcomeUpdate = async (interventionId: number, outcome: string) => {
    try {
      await apiClient.interventions.updateOutcome(interventionId, outcome);
      loadData();
    } catch (error) {
      console.error("Error updating outcome:", error);
      alert("Failed to update intervention outcome.");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background py-12">
        <div className="container mx-auto px-4 max-w-6xl">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!commitment) {
    return (
      <div className="min-h-screen bg-background py-12">
        <div className="container mx-auto px-4 max-w-6xl">
          <p className="text-foreground">Commitment not found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-12">
      <div className="container mx-auto px-4 max-w-6xl space-y-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="flex items-center justify-between"
        >
          <Link href="/">
            <Button variant="outline">← Back to Dashboard</Button>
          </Link>
        </motion.div>

        <CommitmentCard commitment={commitment} />

        {interventions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="space-y-4"
          >
            <h2 className="text-section-heading">Interventions</h2>
            {interventions.map((intervention) => (
              <InterventionAlert
                key={intervention.id}
                intervention={intervention}
                onOutcomeUpdate={handleOutcomeUpdate}
              />
            ))}
          </motion.div>
        )}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <SpendingTracker
            commitmentId={commitmentId}
            spendingLogs={spendingLogs}
            onSpendingAdded={handleSpendingAdded}
          />
        </motion.div>

        {evaluation && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.3 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="text-section-heading">Evaluation Metrics</CardTitle>
                <CardDescription className="text-base">
                  Performance tracking and adherence metrics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  <MetricStat
                    label="Adherence Rate"
                    value={`${evaluation.adherence_rate.toFixed(1)}%`}
                  />
                  <MetricStat
                    label="Weeks Tracked"
                    value={evaluation.weeks_tracked}
                  />
                  <MetricStat
                    label="Weeks Compliant"
                    value={evaluation.weeks_compliant}
                  />
                  {evaluation.intervention_success_rate !== null && evaluation.intervention_success_rate !== undefined && (
                    <MetricStat
                      label="Intervention Success"
                      value={`${evaluation.intervention_success_rate.toFixed(1)}%`}
                    />
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {drift && drift.has_drift && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.4 }}
          >
            <Card className="border-secondary/40">
              <CardHeader>
                <CardTitle className="text-section-heading">Drift Detected</CardTitle>
                <CardDescription className="text-base">
                  {drift.description || "Spending pattern deviation detected"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <InterventionBadge
                      intervention={{
                        id: 0,
                        commitment_id: commitmentId,
                        type: "gentle_warning",
                        message: "",
                        drift_type: drift.drift_type,
                        triggered_at: new Date().toISOString(),
                      }}
                    />
                    {drift.severity && (
                      <>
                        <span className="text-muted-foreground">•</span>
                        <span className="text-sm text-muted-foreground capitalize">
                          {drift.severity}
                        </span>
                      </>
                    )}
                  </div>
                  {drift.deviation_amount && (
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Deviation Amount</p>
                      <p className="text-xl font-semibold text-secondary">
                        ${drift.deviation_amount.toFixed(2)}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  );
}
