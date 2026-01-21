"use client";

import { useState, useEffect, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MetricStat } from "@/components/MetricStat";
import { apiClient, Evaluation, Intervention, Commitment } from "@/lib/api";
import Link from "next/link";

function EvaluationPageContent() {
  const searchParams = useSearchParams();
  const commitmentId = searchParams?.get("commitment_id") 
    ? parseInt(searchParams.get("commitment_id") as string) 
    : null;

  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [commitments, setCommitments] = useState<Commitment[]>([]);
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadCommitments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const commitmentsData = await apiClient.commitments.list();
      setCommitments(commitmentsData);
    } catch (err) {
      console.error("Error loading commitments:", err);
      setError("Failed to load commitments. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  const loadEvaluation = useCallback(async () => {
    if (!commitmentId) {
      await loadCommitments();
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const [evaluationData, interventionsData] = await Promise.all([
        apiClient.commitments.getEvaluation(commitmentId).catch((err: any) => {
          // 404 is expected if no evaluation exists yet - don't treat as error
          if (err.response?.status === 404 || err.response?.status === undefined) {
            return null;
          }
          console.error("Error fetching evaluation:", err);
          return null;
        }),
        apiClient.commitments.getInterventions(commitmentId).catch(() => []),
      ]);
      setEvaluation(evaluationData);
      setInterventions(interventionsData || []);
    } catch (err: any) {
      console.error("Error loading evaluation:", err);
      if (err.response?.status !== 404) {
        setError("Failed to load evaluation data.");
      }
    } finally {
      setLoading(false);
    }
  }, [commitmentId, loadCommitments]);

  useEffect(() => {
    loadEvaluation();
  }, [loadEvaluation]);

  const handleRunEvaluation = async () => {
    if (!commitmentId) return;

    try {
      setEvaluating(true);
      setError(null);
      const newEvaluation = await apiClient.commitments.triggerEvaluation(commitmentId);
      setEvaluation(newEvaluation);
      // Reload interventions to get latest data
      const interventionsData = await apiClient.commitments.getInterventions(commitmentId);
      setInterventions(interventionsData);
    } catch (err) {
      console.error("Error running evaluation:", err);
      setError("Failed to run evaluation. Please try again.");
    } finally {
      setEvaluating(false);
    }
  };

  if (!commitmentId) {
    return (
      <div className="min-h-screen bg-background py-12">
        <div className="container mx-auto px-4 max-w-6xl space-y-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center space-y-3"
          >
            <h1 className="text-page-title">Evaluation Dashboard</h1>
            <p className="text-xl text-muted-foreground">
              Select a commitment to view AI-evaluated metrics
            </p>
          </motion.div>

          {loading ? (
            <p className="text-muted-foreground text-center">Loading commitments...</p>
          ) : error ? (
            <Card>
              <CardContent className="pt-6 text-center">
                <p className="text-destructive mb-4">{error}</p>
                <Button onClick={loadCommitments}>Retry</Button>
              </CardContent>
            </Card>
          ) : commitments.length === 0 ? (
            <Card>
              <CardContent className="pt-6 text-center">
                <p className="text-muted-foreground mb-4">
                  No commitments found. Create a commitment first.
                </p>
                <Link href="/goals/new">
                  <Button>Create Commitment</Button>
                </Link>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {commitments.map((commitment, index) => (
                <motion.div
                  key={commitment.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                >
                  <Link href={`/evaluation?commitment_id=${commitment.id}`}>
                    <Card className="h-full transition-all duration-300 hover:shadow-2xl hover:shadow-primary/20 cursor-pointer">
                      <CardHeader>
                        <CardTitle className="text-xl">
                          ${commitment.goal_amount.toLocaleString()} Goal
                        </CardTitle>
                        <CardDescription>
                          {commitment.goal_timeframe_weeks} weeks
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2 mb-4">
                          <p className="text-sm text-muted-foreground">
                            <span className="font-medium">Weekly Target:</span> $
                            {commitment.weekly_target.toFixed(2)}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            <span className="font-medium">Spending Ceiling:</span> $
                            {commitment.spending_ceiling.toFixed(2)}
                          </p>
                        </div>
                        <Button variant="outline" className="w-full">
                          View Evaluation
                        </Button>
                      </CardContent>
                    </Card>
                  </Link>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  const snapshot = evaluation?.evaluation_snapshot;
  // Handle both nested and flat structure for behavioral recovery score
  const behavioralRecovery = (() => {
    // If snapshot has behavioral_recovery_score as an object
    if (snapshot?.behavioral_recovery_score && typeof snapshot.behavioral_recovery_score === 'object' && 'score' in snapshot.behavioral_recovery_score) {
      return {
        score: typeof snapshot.behavioral_recovery_score.score === 'number' ? snapshot.behavioral_recovery_score.score : 0,
        interpretation: snapshot.behavioral_recovery_score.interpretation || evaluation?.behavioral_recovery_interpretation || "",
        confidence: typeof snapshot.behavioral_recovery_score.confidence === 'number' ? snapshot.behavioral_recovery_score.confidence : 0,
      };
    }
    // If snapshot has behavioral_recovery_score as a number (flat structure)
    if (snapshot?.behavioral_recovery_score && typeof snapshot.behavioral_recovery_score === 'number') {
      return {
        score: snapshot.behavioral_recovery_score,
        interpretation: evaluation?.behavioral_recovery_interpretation || "",
        confidence: 0,
      };
    }
    // Fallback to evaluation fields
    return {
      score: typeof evaluation?.behavioral_recovery_score === 'number' ? evaluation.behavioral_recovery_score : 0,
      interpretation: evaluation?.behavioral_recovery_interpretation || "",
      confidence: 0,
    };
  })();

  return (
    <div className="min-h-screen bg-background py-12">
      <div className="container mx-auto px-4 max-w-6xl space-y-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center space-y-3"
        >
          <h1 className="text-page-title">Evaluation Dashboard</h1>
          <p className="text-xl text-muted-foreground">
            Agent performance metrics and intervention analytics
          </p>
          <p className="text-sm text-muted-foreground italic">
            Metrics evaluated by AI agent using Gemini and tracked via Opik
          </p>
        </motion.div>

        {error && (
          <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 text-destructive">
            {error}
          </div>
        )}

        <div className="flex justify-end">
          <Button
            onClick={handleRunEvaluation}
            disabled={evaluating || loading}
            className="min-w-[150px]"
          >
            {evaluating ? "Running Evaluation..." : "Run Evaluation"}
          </Button>
        </div>

        {loading ? (
          <p className="text-muted-foreground text-center">Loading evaluation data...</p>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* Behavioral Recovery Score - Primary Metric - Always Display */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="md:col-span-2 lg:col-span-3"
            >
              <Card className="border-primary/20 bg-primary/5">
                <CardHeader>
                  <CardTitle className="text-2xl">Behavioral Recovery Score</CardTitle>
                  <CardDescription className="text-base">
                    AI-evaluated measure of recovery effectiveness after interventions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {!evaluation ? (
                    <div className="text-center py-8">
                      <p className="text-muted-foreground mb-4">
                        No evaluation data available. Run evaluation to see Behavioral Recovery Score.
                      </p>
                      <Button onClick={handleRunEvaluation} disabled={evaluating}>
                        {evaluating ? "Running..." : "Run First Evaluation"}
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="flex items-center gap-4">
                        <div className="text-6xl font-bold text-primary">
                          {behavioralRecovery.score || 0}
                        </div>
                        <div className="flex-1">
                          <p className="text-sm text-muted-foreground mb-2">Score (0-100)</p>
                          <p className="text-base">
                            {behavioralRecovery.interpretation || "No interpretation available"}
                          </p>
                          {behavioralRecovery.confidence && behavioralRecovery.confidence > 0 && (
                            <p className="text-xs text-muted-foreground mt-2">
                              Confidence: {(behavioralRecovery.confidence * 100).toFixed(0)}%
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>

            {!evaluation ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.1 }}
                className="md:col-span-2 lg:col-span-3"
              >
                <Card>
                  <CardContent className="pt-6 text-center">
                    <p className="text-muted-foreground mb-4">
                      Run an evaluation to see comprehensive AI-evaluated metrics including adherence rate, intervention success, and agent performance.
                    </p>
                    <Button onClick={handleRunEvaluation} disabled={evaluating} size="lg">
                      {evaluating ? "Running Evaluation..." : "Run Evaluation"}
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ) : (
              <>
                {/* Overall Adherence Rate */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4 }}
                >
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">Overall Adherence Rate</CardTitle>
                  <CardDescription className="text-base">
                    Percentage of weeks meeting savings targets
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <MetricStat
                    label=""
                    value={`${(evaluation.adherence_rate || 0).toFixed(1)}%`}
                    description={
                      snapshot?.adherence?.trend
                        ? `Trend: ${snapshot.adherence.trend}`
                        : evaluation.adherence_trend
                        ? `Trend: ${evaluation.adherence_trend}`
                        : `Based on ${evaluation.weeks_tracked} weeks tracked`
                    }
                  />
                  {(snapshot?.adherence?.confidence || evaluation.adherence_confidence) && (
                    <p className="text-xs text-muted-foreground mt-2">
                      Confidence: {((snapshot?.adherence?.confidence || evaluation.adherence_confidence || 0) * 100).toFixed(0)}%
                    </p>
                  )}
                </CardContent>
              </Card>
                </motion.div>

                {/* Intervention Success Rate */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.1 }}
                >
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">Intervention Success Rate</CardTitle>
                  <CardDescription className="text-base">
                    Percentage of successful interventions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <MetricStat
                    label=""
                    value={
                      evaluation.intervention_success_rate !== undefined && evaluation.intervention_success_rate !== null
                        ? `${evaluation.intervention_success_rate.toFixed(1)}%`
                        : "N/A"
                    }
                    description={
                      evaluation.total_interventions > 0
                        ? `${evaluation.total_interventions} intervention${evaluation.total_interventions !== 1 ? "s" : ""}`
                        : "No interventions yet"
                    }
                  />
                  {snapshot?.interventions?.justification && (
                    <p className="text-xs text-muted-foreground mt-2 italic">
                      {snapshot.interventions.justification}
                    </p>
                  )}
                </CardContent>
              </Card>
                </motion.div>

                {/* False Positive Rate */}
                <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.2 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">False Positive Rate</CardTitle>
                  <CardDescription className="text-base">
                    Interventions that were unnecessary
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <MetricStat
                    label=""
                    value={
                      evaluation.total_interventions > 0 && evaluation.false_positive_interventions !== null && evaluation.false_positive_interventions !== undefined
                        ? `${((evaluation.false_positive_interventions / evaluation.total_interventions) * 100).toFixed(1)}%`
                        : "0%"
                    }
                    description={`${evaluation.false_positive_interventions || 0} false positive${(evaluation.false_positive_interventions || 0) !== 1 ? "s" : ""} detected`}
                  />
                </CardContent>
              </Card>
            </motion.div>

                {/* Intervention Breakdown */}
                {interventions.length > 0 && (
                  <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.3 }}
                className="md:col-span-2 lg:col-span-3"
              >
                <Card>
                  <CardHeader>
                    <CardTitle className="text-section-heading">Intervention Breakdown</CardTitle>
                    <CardDescription className="text-base">
                      Detailed intervention analytics
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {interventions.map((intervention) => (
                        <div
                          key={intervention.id}
                          className="flex justify-between items-center p-4 border border-white/5 rounded-lg bg-muted/10"
                        >
                          <div>
                            <p className="font-medium capitalize">
                              {intervention.type.replace("_", " ")}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              {intervention.drift_type
                                ? `${intervention.drift_type} drift detected`
                                : "Drift detected"}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">
                              {new Date(intervention.triggered_at).toLocaleDateString()}
                            </p>
                          </div>
                          <div className="text-right">
                            <p
                              className={`font-bold ${
                                intervention.outcome === "success"
                                  ? "text-primary"
                                  : intervention.outcome === "failed"
                                  ? "text-destructive"
                                  : "text-muted-foreground"
                              }`}
                            >
                              {intervention.outcome
                                ? intervention.outcome.charAt(0).toUpperCase() +
                                  intervention.outcome.slice(1)
                                : "Pending"}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              {intervention.outcome === "success"
                                ? "User improved"
                                : intervention.outcome === "failed"
                                ? "No improvement"
                                : "Awaiting outcome"}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}

                {/* Drift Detection Metrics */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.4 }}
                  className="md:col-span-2 lg:col-span-3"
                >
              <Card>
                <CardHeader>
                  <CardTitle className="text-section-heading">Drift Detection Metrics</CardTitle>
                  <CardDescription className="text-base">
                    Pattern analysis and deviation tracking
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-6">
                    <MetricStat
                      label="Volume Drifts"
                      value={
                        snapshot?.drift_analysis?.volume_drifts?.toString() ||
                        evaluation.total_interventions.toString()
                      }
                    />
                    <MetricStat
                      label="Timing Drifts"
                      value={
                        snapshot?.drift_analysis?.timing_drifts?.toString() || "0"
                      }
                    />
                    <MetricStat
                      label="Consistency Drifts"
                      value={
                        snapshot?.drift_analysis?.consistency_drifts?.toString() || "0"
                      }
                    />
                  </div>
                  {snapshot?.drift_analysis?.classification_confidence && (
                    <p className="text-xs text-muted-foreground mt-4">
                      Classification Confidence:{" "}
                      {(snapshot.drift_analysis.classification_confidence * 100).toFixed(0)}%
                    </p>
                  )}
                </CardContent>
              </Card>
                </motion.div>

                {/* Agent Performance */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.5 }}
                  className="md:col-span-2 lg:col-span-3"
                >
              <Card>
                <CardHeader>
                  <CardTitle className="text-section-heading">Agent Performance</CardTitle>
                  <CardDescription className="text-base">
                    AI-evaluated agent performance metrics
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {(snapshot?.agent_performance?.planning_accuracy ||
                      evaluation.planning_accuracy) && (
                      <div className="flex justify-between items-center py-2 border-b border-white/5">
                        <span className="text-sm text-muted-foreground">
                          Planning Agent Accuracy
                        </span>
                        <span className="font-semibold">
                          {(
                            (snapshot?.agent_performance?.planning_accuracy ||
                              evaluation.planning_accuracy ||
                              0) * 100
                          ).toFixed(0)}
                          %
                        </span>
                      </div>
                    )}
                    {(snapshot?.agent_performance?.drift_detection_precision ||
                      evaluation.drift_detection_precision) && (
                      <div className="flex justify-between items-center py-2 border-b border-white/5">
                        <span className="text-sm text-muted-foreground">
                          Drift Detection Precision
                        </span>
                        <span className="font-semibold">
                          {(
                            (snapshot?.agent_performance?.drift_detection_precision ||
                              evaluation.drift_detection_precision ||
                              0) * 100
                          ).toFixed(0)}
                          %
                        </span>
                      </div>
                    )}
                    {(snapshot?.agent_performance?.intervention_timing ||
                      evaluation.intervention_timing) && (
                      <div className="flex justify-between items-center py-2">
                        <span className="text-sm text-muted-foreground">Intervention Timing</span>
                        <span className="font-semibold text-primary capitalize">
                          {snapshot?.agent_performance?.intervention_timing ||
                            evaluation.intervention_timing ||
                            "Unknown"}
                        </span>
                      </div>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mt-6">
                    * Metrics evaluated by AI agent using Gemini and tracked via Opik
                    observability integration
                  </p>
                </CardContent>
              </Card>
            </motion.div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function EvaluationPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background py-12">
        <div className="container mx-auto px-4 max-w-6xl text-center">
          <h1 className="text-page-title mb-4">Evaluation Dashboard</h1>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    }>
      <EvaluationPageContent />
    </Suspense>
  );
}
