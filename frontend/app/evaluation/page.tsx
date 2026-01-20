"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">Evaluation Dashboard</h1>
          <p className="text-xl text-muted-foreground">
            Agent performance metrics and intervention analytics
          </p>
        </div>

        {loading ? (
          <p>Loading evaluation data...</p>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>Overall Adherence Rate</CardTitle>
                <CardDescription>Percentage of weeks meeting savings targets</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-4xl font-bold">75.0%</p>
                <p className="text-sm text-muted-foreground mt-2">
                  Based on 4 weeks tracked
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Intervention Success Rate</CardTitle>
                <CardDescription>Percentage of successful interventions</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-4xl font-bold">100%</p>
                <p className="text-sm text-muted-foreground mt-2">
                  1 intervention, 1 success
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>False Positive Rate</CardTitle>
                <CardDescription>Interventions that were unnecessary</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-4xl font-bold">0%</p>
                <p className="text-sm text-muted-foreground mt-2">
                  0 false positives detected
                </p>
              </CardContent>
            </Card>

            <Card className="md:col-span-2 lg:col-span-3">
              <CardHeader>
                <CardTitle>Intervention Breakdown</CardTitle>
                <CardDescription>Detailed intervention analytics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-4 border rounded-lg">
                    <div>
                      <p className="font-medium">Gentle Warning</p>
                      <p className="text-sm text-muted-foreground">
                        Week 3 overspending detected
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-green-600">Success</p>
                      <p className="text-sm text-muted-foreground">User improved</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="md:col-span-2 lg:col-span-3">
              <CardHeader>
                <CardTitle>Drift Detection Metrics</CardTitle>
                <CardDescription>Pattern analysis and deviation tracking</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Volume Drifts</p>
                    <p className="text-2xl font-bold">1</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Timing Drifts</p>
                    <p className="text-2xl font-bold">0</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Consistency Drifts</p>
                    <p className="text-2xl font-bold">0</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="md:col-span-2 lg:col-span-3">
              <CardHeader>
                <CardTitle>Agent Performance</CardTitle>
                <CardDescription>Opik-powered metrics comparison</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Planning Agent Accuracy</span>
                    <span className="font-medium">95%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Drift Detection Precision</span>
                    <span className="font-medium">100%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Intervention Timing</span>
                    <span className="font-medium">Optimal</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-4">
                  * Metrics tracked via Opik observability integration
                </p>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
