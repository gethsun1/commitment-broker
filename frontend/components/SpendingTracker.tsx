"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient, Spending, SpendingInput } from "@/lib/api";
import { format } from "date-fns";

interface SpendingTrackerProps {
  commitmentId: number;
  spendingLogs: Spending[];
  onSpendingAdded: () => void;
}

export function SpendingTracker({
  commitmentId,
  spendingLogs,
  onSpendingAdded,
}: SpendingTrackerProps) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<SpendingInput>({
    commitment_id: commitmentId,
    amount: 0,
    category: "",
    week_number: 1,
    description: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await apiClient.spending.add(formData);
      setFormData({
        commitment_id: commitmentId,
        amount: 0,
        category: "",
        week_number: formData.week_number,
        description: "",
      });
      onSpendingAdded();
    } catch (error) {
      console.error("Error adding spending:", error);
      alert("Failed to add spending. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Track Spending</CardTitle>
          <CardDescription>Log your weekly spending to track adherence to your commitment.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="week_number">Week Number</Label>
                <Input
                  id="week_number"
                  type="number"
                  min="1"
                  value={formData.week_number || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      week_number: parseInt(e.target.value) || 1,
                    })
                  }
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="amount">Amount ($)</Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.amount || ""}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      amount: parseFloat(e.target.value) || 0,
                    })
                  }
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="category">Category (Optional)</Label>
              <Input
                id="category"
                value={formData.category}
                onChange={(e) =>
                  setFormData({ ...formData, category: e.target.value })
                }
                placeholder="e.g., Groceries, Entertainment"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description (Optional)</Label>
              <Input
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder="Brief description"
              />
            </div>

            <Button type="submit" disabled={loading}>
              {loading ? "Adding..." : "Add Spending"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {spendingLogs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Spending History</CardTitle>
            <CardDescription>Your logged spending entries</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {spendingLogs.map((spending) => (
                <div
                  key={spending.id}
                  className="flex justify-between items-center p-3 border rounded-lg"
                >
                  <div>
                    <p className="font-medium">Week {spending.week_number}</p>
                    <p className="text-sm text-muted-foreground">
                      {spending.category && `${spending.category} • `}
                      {format(new Date(spending.created_at), "MMM d, yyyy")}
                    </p>
                    {spending.description && (
                      <p className="text-sm text-muted-foreground mt-1">
                        {spending.description}
                      </p>
                    )}
                  </div>
                  <p className="text-lg font-semibold">${spending.amount.toFixed(2)}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
