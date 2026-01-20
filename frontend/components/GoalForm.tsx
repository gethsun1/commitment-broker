"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient, GoalInput } from "@/lib/api";

export function GoalForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<GoalInput>({
    goal_description: "",
    target_amount: 0,
    timeframe: "",
    income_frequency: "monthly",
    risk_moments: [],
    user_id: "demo_user",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const commitment = await apiClient.goals.create(formData);
      router.push(`/commitments/${commitment.id}`);
    } catch (error) {
      console.error("Error creating goal:", error);
      alert("Failed to create goal. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Create Financial Goal</CardTitle>
        <CardDescription>
          Enter your financial goal and let our AI agent create a personalized commitment plan.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="goal_description">Goal Description</Label>
            <Input
              id="goal_description"
              value={formData.goal_description}
              onChange={(e) =>
                setFormData({ ...formData, goal_description: e.target.value })
              }
              placeholder="e.g., Save for vacation, Emergency fund"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="target_amount">Target Amount ($)</Label>
            <Input
              id="target_amount"
              type="number"
              step="0.01"
              min="0"
              value={formData.target_amount || ""}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  target_amount: parseFloat(e.target.value) || 0,
                })
              }
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="timeframe">Timeframe</Label>
            <Input
              id="timeframe"
              value={formData.timeframe}
              onChange={(e) =>
                setFormData({ ...formData, timeframe: e.target.value })
              }
              placeholder="e.g., 6 months, 1 year"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="income_frequency">Income Frequency</Label>
            <select
              id="income_frequency"
              value={formData.income_frequency}
              onChange={(e) =>
                setFormData({ ...formData, income_frequency: e.target.value })
              }
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              required
            >
              <option value="weekly">Weekly</option>
              <option value="biweekly">Biweekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="risk_moments">Risk Moments (Optional)</Label>
            <Input
              id="risk_moments"
              value={formData.risk_moments?.join(", ") || ""}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  risk_moments: e.target.value
                    .split(",")
                    .map((s) => s.trim())
                    .filter(Boolean),
                })
              }
              placeholder="e.g., Payday, End of month"
            />
          </div>

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Creating Goal..." : "Create Goal & Generate Commitment Plan"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
