"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { CommitmentCard } from "@/components/CommitmentCard";
import { SpendingTracker } from "@/components/SpendingTracker";
import { InterventionAlert } from "@/components/InterventionAlert";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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

  useEffect(() => {
    loadData();
  }, [commitmentId]);

  const loadData = async () => {
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
  };

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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
        <div className="max-w-6xl mx-auto">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!commitment) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
        <div className="max-w-6xl mx-auto">
          <p>Commitment not found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <Link href="/">
              <Button variant="outline">← Back to Dashboard</Button>
            </Link>
          </div>
        </div>

        <CommitmentCard commitment={commitment} />

        {interventions.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold">Interventions</h2>
            {interventions.map((intervention) => (
              <InterventionAlert
                key={intervention.id}
                intervention={intervention}
                onOutcomeUpdate={handleOutcomeUpdate}
              />
            ))}
          </div>
        )}

        <SpendingTracker
          commitmentId={commitmentId}
          spendingLogs={spendingLogs}
          onSpendingAdded={handleSpendingAdded}
        />

        {evaluation && (
          <Card>
            <CardHeader>
              <CardTitle>Evaluation Metrics</CardTitle>
              <CardDescription>Performance tracking and adherence metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Adherence Rate</p>
                  <p className="text-2xl font-bold">{evaluation.adherence_rate.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Weeks Tracked</p>
                  <p className="text-2xl font-bold">{evaluation.weeks_tracked}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Weeks Compliant</p>
                  <p className="text-2xl font-bold">{evaluation.weeks_compliant}</p>
                </div>
                {evaluation.intervention_success_rate !== null && (
                  <div>
                    <p className="text-sm text-muted-foreground">Intervention Success</p>
                    <p className="text-2xl font-bold">
                      {evaluation.intervention_success_rate.toFixed(1)}%
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {drift && drift.has_drift && (
          <Card className="border-orange-500">
            <CardHeader>
              <CardTitle>Drift Detected</CardTitle>
              <CardDescription>
                {drift.description || "Spending pattern deviation detected"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-sm">
                  <span className="font-medium">Type:</span> {drift.drift_type}
                </p>
                {drift.severity && (
                  <p className="text-sm">
                    <span className="font-medium">Severity:</span> {drift.severity}
                  </p>
                )}
                {drift.deviation_amount && (
                  <p className="text-sm">
                    <span className="font-medium">Deviation:</span> $
                    {drift.deviation_amount.toFixed(2)}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
