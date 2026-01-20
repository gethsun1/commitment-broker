"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { CommitmentLoop } from "@/components/svgs/CommitmentLoop";
import { apiClient, Commitment } from "@/lib/api";

export default function Home() {
  const [commitments, setCommitments] = useState<Commitment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real app, you'd fetch all commitments for the user
    // For now, this is a placeholder
    setLoading(false);
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 lg:py-32">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              className="space-y-8"
            >
              <div className="space-y-4">
                <motion.h1
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.8 }}
                  className="text-page-title gradient-text"
                >
                  Commitment Broker
                </motion.h1>
                <motion.h2
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.8, delay: 0.2 }}
                  className="text-2xl font-medium text-foreground/90"
                >
                  Turn financial intentions into measurable commitments
                </motion.h2>
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.8, delay: 0.4 }}
                  className="text-base text-muted-foreground leading-relaxed max-w-xl"
                >
                  An AI system that plans, observes, intervenes, and learns so your goals don't fade.
                </motion.p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <Link href="/goals/new">
                  <Button size="lg" className="h-12 px-8 text-base">
                    Create Commitment
                  </Button>
                </Link>
                <Link href="/evaluation">
                  <Button variant="ghost" size="lg" className="h-12 px-8 text-base">
                    View Demo Journey
                  </Button>
                </Link>
              </div>
            </motion.div>

            {/* Right Column - SVG Visualization */}
            <motion.div
              initial={{ opacity: 0, x: 20, rotateY: -15 }}
              animate={{ opacity: 1, x: 0, rotateY: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              whileHover={{ rotateY: 5, scale: 1.02 }}
              className="flex items-center justify-center transform-3d"
            >
              <div className="w-full max-w-md relative">
                <div className="absolute inset-0 bg-gradient-to-r from-primary/20 via-secondary/20 to-accent/20 rounded-full blur-3xl animate-pulse-glow" />
                <div className="relative">
                  <CommitmentLoop />
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Commitments Grid */}
      {commitments.length > 0 && (
        <section className="container mx-auto px-4 py-16">
          <div className="max-w-6xl mx-auto space-y-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <h2 className="text-section-heading mb-8">Your Commitments</h2>
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {commitments.map((commitment, index) => (
                  <motion.div
                    key={commitment.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: 0.1 * index }}
                    whileHover={{ y: -8, scale: 1.02, rotateY: 2 }}
                    className="transform-3d"
                  >
                    <Link href={`/commitments/${commitment.id}`}>
                      <Card className="h-full transition-all duration-300 hover:shadow-2xl hover:shadow-primary/20 hover:glow-primary cursor-pointer relative overflow-hidden group">
                      <CardHeader>
                        <CardTitle className="text-xl">
                          ${commitment.goal_amount.toLocaleString()} Goal
                        </CardTitle>
                        <CardDescription>
                          {commitment.goal_timeframe_weeks} weeks remaining
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="space-y-2">
                          <p className="text-sm text-muted-foreground">
                            <span className="font-medium">Weekly Target:</span> $
                            {commitment.weekly_target.toFixed(2)}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            <span className="font-medium">Spending Ceiling:</span> $
                            {commitment.spending_ceiling.toFixed(2)}
                          </p>
                        </div>
                        <Button variant="outline" className="w-full mt-4">
                          View Details
                        </Button>
                      </CardContent>
                    </Card>
                    </Link>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </section>
      )}

      {/* Empty State */}
      {commitments.length === 0 && !loading && (
        <section className="container mx-auto px-4 py-16">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="max-w-md mx-auto"
            >
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl">Get Started</CardTitle>
                  <CardDescription className="text-base">
                    Create your first financial goal to begin tracking your commitments.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/goals/new">
                    <Button className="w-full">Create Goal</Button>
                  </Link>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </section>
      )}
    </div>
  );
}
