"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Commitment } from "@/lib/api";
import { format } from "date-fns";

interface CommitmentCardProps {
  commitment: Commitment;
}

export function CommitmentCard({ commitment }: CommitmentCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Your Commitment Plan</CardTitle>
        <CardDescription>
          Created on {format(new Date(commitment.created_at), "MMM d, yyyy")}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Goal Amount</p>
            <p className="text-2xl font-bold">${commitment.goal_amount.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Timeframe</p>
            <p className="text-2xl font-bold">{commitment.goal_timeframe_weeks} weeks</p>
          </div>
        </div>

        <div className="border-t pt-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Weekly Savings Target</p>
              <p className="text-xl font-semibold text-green-600">
                ${commitment.weekly_target.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Weekly Spending Ceiling</p>
              <p className="text-xl font-semibold text-orange-600">
                ${commitment.spending_ceiling.toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        <div className="border-t pt-4">
          <p className="text-sm text-muted-foreground">Income Frequency</p>
          <p className="font-medium capitalize">{commitment.income_frequency}</p>
        </div>
      </CardContent>
    </Card>
  );
}
