"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SegmentedControl } from "@/components/ui/segmented-control";
import { TagInput } from "@/components/ui/tag-input";
import { apiClient, GoalInput } from "@/lib/api";
import { Loader2 } from "lucide-react";

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

  // Convert timeframe months to the format expected by backend
  const handleTimeframeChange = (months: string) => {
    setFormData({ ...formData, timeframe: `${months} months` });
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-page-title">Create a Financial Commitment</CardTitle>
        <CardDescription className="text-base mt-2">
          Define the intention. The system handles the structure.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Goal Description */}
          <div className="space-y-3">
            <Label htmlFor="goal_description" className="text-sm font-medium">
              Goal Description
            </Label>
            <Input
              id="goal_description"
              value={formData.goal_description}
              onChange={(e) =>
                setFormData({ ...formData, goal_description: e.target.value })
              }
              placeholder="e.g., Save for vacation, Emergency fund"
              className="h-12 text-base placeholder:italic"
              required
            />
            <p className="text-xs text-muted-foreground">
              Describe your financial goal in clear, specific terms
            </p>
          </div>

          {/* Target Amount */}
          <div className="space-y-3">
            <Label htmlFor="target_amount" className="text-sm font-medium">
              Target Amount
            </Label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-lg text-muted-foreground">
                $
              </span>
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
                className="h-14 text-lg text-right pl-10 pr-4 font-semibold"
                placeholder="0.00"
                required
              />
            </div>
            <p className="text-xs text-muted-foreground">
              Total amount you want to save
            </p>
          </div>

          {/* Timeframe */}
          <div className="space-y-3">
            <Label htmlFor="timeframe" className="text-sm font-medium">
              Timeframe
            </Label>
            <select
              id="timeframe"
              value={
                formData.timeframe.includes("3")
                  ? "3"
                  : formData.timeframe.includes("6")
                  ? "6"
                  : formData.timeframe.includes("12")
                  ? "12"
                  : ""
              }
              onChange={(e) => handleTimeframeChange(e.target.value)}
              className="flex h-12 w-full rounded-md border border-input bg-background px-4 py-2 text-base ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              required
            >
              <option value="">Select timeframe</option>
              <option value="3">3 months</option>
              <option value="6">6 months</option>
              <option value="12">12 months</option>
            </select>
            <p className="text-xs text-muted-foreground">
              How long to achieve this goal
            </p>
          </div>

          {/* Income Frequency */}
          <div className="space-y-3">
            <Label className="text-sm font-medium">Income Frequency</Label>
            <SegmentedControl
              options={[
                { value: "weekly", label: "Weekly" },
                { value: "biweekly", label: "Bi-Weekly" },
                { value: "monthly", label: "Monthly" },
              ]}
              value={formData.income_frequency}
              onChange={(value) =>
                setFormData({ ...formData, income_frequency: value })
              }
            />
            <p className="text-xs text-muted-foreground">
              How often you receive income
            </p>
          </div>

          {/* Risk Moments */}
          <div className="space-y-3">
            <Label className="text-sm font-medium">Risk Moments (Optional)</Label>
            <TagInput
              value={formData.risk_moments || []}
              onChange={(tags) =>
                setFormData({ ...formData, risk_moments: tags })
              }
              suggestions={["Payday", "End of Month", "Weekends"]}
              placeholder="Add risk moments when spending is likely..."
            />
            <p className="text-xs text-muted-foreground">
              Times when you're most likely to overspend
            </p>
          </div>

          {/* Submit Button */}
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full"
          >
            <Button
              type="submit"
              disabled={loading}
              className="w-full h-14 text-base font-semibold bg-gradient-to-r from-primary via-secondary to-primary/90 hover:from-primary/90 hover:via-secondary/90 hover:to-primary relative overflow-hidden group shimmer"
            >
              <span className="relative z-10 flex items-center justify-center gap-3">
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>Creating Commitment Plan...</span>
                  </>
                ) : (
                  "Create Commitment Plan"
                )}
              </span>
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                initial={{ x: "-100%" }}
                animate={{ x: "100%" }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              />
            </Button>
          </motion.div>
        </form>
      </CardContent>
    </Card>
  );
}
