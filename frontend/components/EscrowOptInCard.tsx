"use client";

import { useState, useEffect } from "react";
import { useAccount, useSwitchChain, useWriteContract, useReadContract, useWaitForTransactionReceipt } from "wagmi";
import { parseEther, formatEther } from "viem";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient, Commitment, EscrowInitResponse } from "@/lib/api";
import { Loader2, Lock } from "lucide-react";
import CommitmentEscrowArtifact from "@/lib/contracts/CommitmentEscrow.json";
import CUSDTArtifact from "@/lib/contracts/CUSDT.json";

const SEPOLIA_CHAIN_ID = 11155111;

interface EscrowOptInCardProps {
  commitment: Commitment;
  onEscrowCreated: () => void;
}

export function EscrowOptInCard({ commitment, onEscrowCreated }: EscrowOptInCardProps) {
  const defaultGoalEquivalent =
    commitment.weekly_target * commitment.goal_timeframe_weeks;
  const [enabled, setEnabled] = useState(true);
  const [amountCusdt, setAmountCusdt] = useState("100");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { address, isConnected, chainId } = useAccount();
  const { switchChainAsync } = useSwitchChain();
  const { writeContractAsync: writeCommitment } = useWriteContract();
  const { writeContractAsync: writeApprove } = useWriteContract();

  // Read allowance
  const { data: allowance, refetch: refetchAllowance } = useReadContract({
    address: CUSDTArtifact.address as `0x${string}`,
    abi: CUSDTArtifact.abi,
    functionName: "allowance",
    args: address ? [address, CommitmentEscrowArtifact.address as `0x${string}`] : undefined,
    query: {
      enabled: !!address && isConnected,
    }
  });

  // Read balance
  const { data: balance } = useReadContract({
    address: CUSDTArtifact.address as `0x${string}`,
    abi: CUSDTArtifact.abi,
    functionName: "balanceOf",
    args: address ? [address] : undefined,
    query: {
      enabled: !!address && isConnected,
    }
  });

  const maturityDate = (() => {
    const created = new Date(commitment.created_at);
    const end = new Date(created);
    end.setDate(end.getDate() + commitment.goal_timeframe_weeks * 7);
    return end;
  })();

  const handleApprove = async () => {
    setError(null);
    if (!isConnected || !address) {
      setError("Connect your wallet first.");
      return;
    }
    if (chainId !== SEPOLIA_CHAIN_ID) {
      try {
        await switchChainAsync?.({ chainId: SEPOLIA_CHAIN_ID });
      } catch (e) {
        setError("Switch to Sepolia to approve.");
        return;
      }
    }

    setLoading(true);
    try {
      const amountWei = parseEther(amountCusdt);
      const txHash = await writeApprove({
        address: CUSDTArtifact.address as `0x${string}`,
        abi: CUSDTArtifact.abi,
        functionName: "approve",
        args: [CommitmentEscrowArtifact.address as `0x${string}`, amountWei],
      });
      // In a real app we'd wait for receipt here, but for quick UI we can just wait a bit or rely on the user to click "Lock" after tx confirms
      // For better UX let's just let the user click Lock when ready, but ideally we show a "Approving..." state that auto-updates using useWaitForTransactionReceipt
    } catch (e: any) {
      setError(e?.message || "Approve failed.");
    } finally {
      setLoading(false);
      // Wait a moment for node to sync then refetch
      setTimeout(refetchAllowance, 5000);
    }
  };

  const handleLockFunds = async () => {
    setError(null);
    if (!enabled) return;
    if (!isConnected || !address) {
      setError("Connect your wallet first.");
      return;
    }
    if (chainId !== SEPOLIA_CHAIN_ID) {
      try {
        await switchChainAsync?.({ chainId: SEPOLIA_CHAIN_ID });
      } catch (e) {
        setError("Switch to Sepolia to lock funds.");
        return;
      }
    }

    setLoading(true);
    try {
      const init = await apiClient.escrow.init(commitment.id) as EscrowInitResponse;
      const amountWei = parseEther(amountCusdt);

      // Double check allowance
      if (!allowance || BigInt(allowance as any) < amountWei) {
        setError("Insufficient allowance. Please approve CUSDT first.");
        setLoading(false);
        return;
      }

      const txHash = await writeCommitment({
        address: init.contract_address as `0x${string}`,
        abi: CommitmentEscrowArtifact.abi as any,
        functionName: "createCommitment",
        args: [init.commitment_id as `0x${string}`, BigInt(init.unlock_timestamp), amountWei],
      });

      if (!txHash) throw new Error("No tx hash");
      await apiClient.escrow.confirm({
        commitment_id: commitment.id,
        wallet_address: address,
        tx_hash: txHash,
        amount: amountWei.toString(),
      });
      onEscrowCreated();
    } catch (e: any) {
      setError(e?.message || "Failed to lock funds. Try again.");
    } finally {
      setLoading(false);
    }
  };

  const amountWei = parseEther(amountCusdt || "0");
  const needsApproval = !allowance || BigInt(allowance as any) < amountWei;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="border-primary/20 bg-primary/5">
        <CardHeader>
          <CardTitle className="text-section-heading flex items-center gap-2">
            <Lock className="h-5 w-5" />
            Enable On-Chain Enforcement (Optional)
          </CardTitle>
          <CardDescription className="text-base">
            Enforce this commitment by locking CUSDT tokens until maturity.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center gap-3">
            <button
              type="button"
              role="switch"
              aria-checked={enabled}
              onClick={() => setEnabled(!enabled)}
              className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ${enabled ? "border-primary bg-primary" : "border-muted-foreground/30 bg-muted"
                }`}
            >
              <span
                className={`pointer-events-none block h-5 w-5 rounded-full bg-white shadow ring-0 transition ${enabled ? "translate-x-5" : "translate-x-0.5"
                  }`}
              />
            </button>
            <Label className="text-sm font-medium">Use escrow</Label>
          </div>

          {enabled && (
            <>
              <div className="space-y-2">
                <div className="flex justify-between items-end">
                  <Label htmlFor="escrow-amount">Amount (CUSDT)</Label>
                  {isConnected && balance !== undefined && (
                    <span className="text-xs text-muted-foreground">
                      Balance: {parseFloat(formatEther(balance as bigint)).toFixed(2)} CUSDT
                    </span>
                  )}
                </div>
                <Input
                  id="escrow-amount"
                  type="text"
                  inputMode="decimal"
                  value={amountCusdt}
                  onChange={(e) => setAmountCusdt(e.target.value)}
                  className="font-mono"
                />
                <p className="text-xs text-muted-foreground">
                  Weekly target: ${commitment.weekly_target}. Total goal: ${defaultGoalEquivalent.toFixed(2)}.
                </p>
              </div>
              <div className="space-y-1">
                <Label className="text-muted-foreground">Maturity date</Label>
                <p className="text-base font-medium">
                  {maturityDate.toLocaleDateString(undefined, {
                    dateStyle: "long",
                  })}
                </p>
              </div>

              <div className="flex gap-2">
                {needsApproval ? (
                  <Button
                    onClick={handleApprove}
                    disabled={loading}
                    className="w-full"
                    variant="secondary"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Approving...
                      </>
                    ) : (
                      "1. Approve CUSDT"
                    )}
                  </Button>
                ) : (
                  <Button
                    onClick={handleLockFunds}
                    disabled={loading}
                    className="w-full"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Locking funds…
                      </>
                    ) : (
                      "2. Lock Funds"
                    )}
                  </Button>
                )}
              </div>
            </>
          )}

          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}

          <div className="space-y-3 border-t border-white/10 pt-4">
            <p className="text-xs text-muted-foreground">
              Funds are locked in the smart contract until the maturity date. You will not be able to withdraw before then.
            </p>
            <div className="bg-destructive/10 border border-destructive/20 rounded-md p-3 space-y-2">
              <p className="text-[10px] font-bold uppercase tracking-wider text-destructive/80">Safety Disclaimers</p>
              <ul className="text-[10px] text-muted-foreground list-disc pl-3 space-y-1">
                <li>This is <strong>not</strong> an investment vehicle and provides <strong>no yield</strong>.</li>
                <li>This is a behavioral discipline tool, not financial or investment advice.</li>
                <li>Avoid using funds required for essential living expenses or emergencies.</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
