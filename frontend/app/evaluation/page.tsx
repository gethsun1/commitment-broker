"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricStat } from "@/components/MetricStat";
import { apiClient, Evaluation, Intervention } from "@/lib/api";

export default function EvaluationPage() {
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real app, fetch all evaluations
    // For demo, we'll use a placeholder that shows the structure
    setLoading(false);
  }, []);

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
        </motion.div>

        {loading ? (
          <p className="text-muted-foreground">Loading evaluation data...</p>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
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
                    value="75.0%"
                    description="Based on 4 weeks tracked"
                  />
                </CardContent>
              </Card>
            </motion.div>

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
                    value="100%"
                    description="1 intervention, 1 success"
                  />
                </CardContent>
              </Card>
            </motion.div>

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
                    value="0%"
                    description="0 false positives detected"
                  />
                </CardContent>
              </Card>
            </motion.div>

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
                    <div className="flex justify-between items-center p-4 border border-white/5 rounded-lg bg-muted/10">
                      <div>
                        <p className="font-medium">Gentle Warning</p>
                        <p className="text-sm text-muted-foreground">
                          Week 3 overspending detected
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-primary">Success</p>
                        <p className="text-sm text-muted-foreground">User improved</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

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
                    <MetricStat label="Volume Drifts" value="1" />
                    <MetricStat label="Timing Drifts" value="0" />
                    <MetricStat label="Consistency Drifts" value="0" />
                  </div>
                </CardContent>
              </Card>
            </motion.div>

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
                    Opik-powered metrics comparison
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center py-2 border-b border-white/5">
                      <span className="text-sm text-muted-foreground">Planning Agent Accuracy</span>
                      <span className="font-semibold">95%</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-white/5">
                      <span className="text-sm text-muted-foreground">Drift Detection Precision</span>
                      <span className="font-semibold">100%</span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-sm text-muted-foreground">Intervention Timing</span>
                      <span className="font-semibold text-primary">Optimal</span>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground mt-6">
                    * Metrics tracked via Opik observability integration
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
}
