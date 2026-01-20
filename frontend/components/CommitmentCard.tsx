"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Commitment } from "@/lib/api";
import { format } from "date-fns";
import { motion } from "framer-motion";
import { MetricStat } from "./MetricStat";

interface CommitmentCardProps {
  commitment: Commitment;
}

export function CommitmentCard({ commitment }: CommitmentCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, rotateX: -10 }}
      animate={{ opacity: 1, y: 0, rotateX: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={{ y: -5, scale: 1.01 }}
      className="transform-3d"
    >
      <Card className="relative overflow-hidden group">
        <CardHeader>
          <CardTitle className="text-page-title">Your Commitment Plan</CardTitle>
          <CardDescription className="text-base">
            Created on {format(new Date(commitment.created_at), "MMM d, yyyy")}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <MetricStat
              label="Goal Amount"
              value={`$${commitment.goal_amount.toLocaleString()}`}
            />
            <MetricStat
              label="Timeframe"
              value={`${commitment.goal_timeframe_weeks} weeks`}
            />
          </div>

          <div className="border-t border-white/5 pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <p className="text-meta-label text-muted-foreground mb-2">
                  Weekly Savings Target
                </p>
                <p className="text-2xl font-semibold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                  ${commitment.weekly_target.toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-meta-label text-muted-foreground mb-2">
                  Weekly Spending Ceiling
                </p>
                <p className="text-2xl font-semibold bg-gradient-to-r from-secondary to-primary bg-clip-text text-transparent">
                  ${commitment.spending_ceiling.toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          <div className="border-t border-white/5 pt-6">
            <p className="text-meta-label text-muted-foreground mb-2">Income Frequency</p>
            <p className="text-base font-medium capitalize">{commitment.income_frequency}</p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
