"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient, Commitment, Evaluation } from "@/lib/api";

export default function Home() {
  const [commitments, setCommitments] = useState<Commitment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real app, you'd fetch all commitments for the user
    // For now, this is a placeholder
    setLoading(false);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">Commitment Broker</h1>
          <p className="text-xl text-muted-foreground">
            Transform your financial goals into enforceable behavioral commitments
          </p>
        </div>

        <div className="flex justify-center gap-4">
          <Link href="/goals/new">
            <Button size="lg">Create New Goal</Button>
          </Link>
        </div>

        {commitments.length === 0 && !loading && (
          <Card className="max-w-md mx-auto">
            <CardHeader>
              <CardTitle>Get Started</CardTitle>
              <CardDescription>
                Create your first financial goal to begin tracking your commitments.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/goals/new">
                <Button className="w-full">Create Goal</Button>
              </Link>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {commitments.map((commitment) => (
            <Card key={commitment.id}>
              <CardHeader>
                <CardTitle>${commitment.goal_amount.toLocaleString()} Goal</CardTitle>
                <CardDescription>
                  {commitment.goal_timeframe_weeks} weeks remaining
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm">
                    <span className="font-medium">Weekly Target:</span> $
                    {commitment.weekly_target.toFixed(2)}
                  </p>
                  <p className="text-sm">
                    <span className="font-medium">Spending Ceiling:</span> $
                    {commitment.spending_ceiling.toFixed(2)}
                  </p>
                </div>
                <Link href={`/commitments/${commitment.id}`}>
                  <Button className="w-full mt-4">View Details</Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
