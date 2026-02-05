"use client";

import { useState, useEffect } from "react";
import { useWriteContract } from "wagmi";
import { formatEther } from "viem";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient, EscrowStatus as EscrowStatusType } from "@/lib/api";
import { Lock, Unlock, Check } from "lucide-react";
import CommitmentEscrowArtifact from "@/lib/contracts/CommitmentEscrow.json";

interface EscrowStatusBadgeProps {
  escrow: EscrowStatusType;
  onWithdrawn?: () => void;
}

function formatCountdown(unlockTimestamp: number): string {
  const now = Math.floor(Date.now() / 1000);
  const remaining = Math.max(0, unlockTimestamp - now);
  if (remaining <= 0) return "Unlocked";
  const d = Math.floor(remaining / 86400);
  const h = Math.floor((remaining % 86400) / 3600);
  const m = Math.floor((remaining % 3600) / 60);
  if (d > 0) return `${d}d ${h}h ${m}m`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

export function EscrowStatusBadge({ escrow, onWithdrawn }: EscrowStatusBadgeProps) {
  const [countdown, setCountdown] = useState("");
  const { writeContractAsync, isPending } = useWriteContract();

  useEffect(() => {
    if (escrow.status !== "LOCKED") return;
    const update = () => setCountdown(formatCountdown(escrow.unlock_timestamp));
    update();
    const t = setInterval(update, 60_000);
    return () => clearInterval(t);
  }, [escrow.status, escrow.unlock_timestamp]);

  const handleWithdraw = async () => {
    try {
      await writeContractAsync({
        address: escrow.contract_address as `0x${string}`,
        abi: CommitmentEscrowArtifact.abi as any,
        functionName: "withdraw",
        args: [escrow.commitment_hash as `0x${string}`],
      });
      await apiClient.escrow.markWithdrawn(escrow.commitment_id);
      onWithdrawn?.();
    } catch (e) {
      console.error("Withdraw failed:", e);
    }
  };

  const amountCusdt = formatEther(BigInt(escrow.amount));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="border-primary/20 bg-primary/5">
        <CardHeader>
          <CardTitle className="text-section-heading flex items-center gap-2">
            {escrow.status === "LOCKED" && <Lock className="h-5 w-5" />}
            {escrow.status === "UNLOCKED" && <Unlock className="h-5 w-5" />}
            {escrow.status === "WITHDRAWN" && <Check className="h-5 w-5" />}
            On-Chain Escrow
          </CardTitle>
          <CardDescription className="text-base">
            {escrow.status === "LOCKED" && "Funds locked until maturity"}
            {escrow.status === "UNLOCKED" && "Withdraw available"}
            {escrow.status === "WITHDRAWN" && "Funds withdrawn"}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            {escrow.status === "LOCKED" && (
              <span className="rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-sm font-medium">
                Locked · {countdown}
              </span>
            )}
            {escrow.status === "UNLOCKED" && (
              <span className="rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-sm font-medium">
                Unlocked
              </span>
            )}
            {escrow.status === "WITHDRAWN" && (
              <span className="rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-sm font-medium">
                Withdrawn
              </span>
            )}
          </div>
          <p className="text-sm text-muted-foreground">
            {amountCusdt} CUSDT · Sepolia
          </p>
          {escrow.status === "UNLOCKED" && (
            <Button onClick={handleWithdraw} disabled={isPending}>
              {isPending ? "Withdrawing…" : "Withdraw"}
            </Button>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
