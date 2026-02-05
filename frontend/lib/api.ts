import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface GoalInput {
  goal_description: string;
  target_amount: number;
  timeframe: string;
  income_frequency: string;
  risk_moments?: string[];
  user_id: string;
}

export interface Commitment {
  id: number;
  goal_id: string;
  user_id: string;
  weekly_target: number;
  spending_ceiling: number;
  goal_amount: number;
  goal_timeframe_weeks: number;
  income_frequency: string;
  version: number;
  created_at: string;
}

export interface SpendingInput {
  commitment_id: number;
  amount: number;
  category?: string;
  week_number: number;
  description?: string;
}

export interface Spending {
  id: number;
  commitment_id: number;
  amount: number;
  category?: string;
  week_number: number;
  description?: string;
  created_at: string;
}

export interface Drift {
  has_drift: boolean;
  drift_type?: string;
  severity?: string;
  description?: string;
  deviation_amount?: number;
}

export interface Intervention {
  id: number;
  commitment_id: number;
  type: "gentle_warning" | "recommitment_prompt" | "goal_renegotiation";
  message: string;
  drift_type?: string;
  triggered_at: string;
  outcome?: string;
}

export interface Evaluation {
  id: number;
  commitment_id: number;
  // Backward compatible fields
  adherence_rate: number;
  intervention_success_rate?: number;
  false_positive_interventions: number;
  total_interventions: number;
  weeks_tracked: number;
  weeks_compliant: number;
  timestamp: string;
  // New AI-generated fields
  evaluation_snapshot?: {
    adherence?: {
      rate: number;
      trend?: string;
      confidence?: number;
    };
    interventions?: {
      success_rate?: number;
      false_positive_rate?: number;
      justification?: string;
    };
    drift_analysis?: {
      volume_drifts?: number;
      timing_drifts?: number;
      consistency_drifts?: number;
      classification_confidence?: number;
    };
    agent_performance?: {
      planning_accuracy?: number;
      drift_detection_precision?: number;
      intervention_timing?: string;
    };
    behavioral_recovery_score?: {
      score: number;
      interpretation?: string;
      confidence?: number;
    };
    escrow_metrics?: {
      escrow_follow_through_rate?: number;
      time_to_withdrawal_days?: number;
      drift_reduction_during_lock?: string;
    };
  };
  behavioral_recovery_score?: number;
  behavioral_recovery_interpretation?: string;
  adherence_trend?: string;
  adherence_confidence?: number;
  intervention_justification?: string;
  drift_classification_confidence?: number;
  planning_accuracy?: number;
  drift_detection_precision?: number;
  intervention_timing?: string;
  average_deviation?: number;
}

export interface EscrowInitResponse {
  commitment_id: string;
  unlock_timestamp: number;
  contract_address: string;
  chain_id: number;
}

export interface EscrowConfirmRequest {
  commitment_id: number;
  wallet_address: string;
  tx_hash: string;
  amount: number | string;
}

export interface EscrowStatus {
  id: number;
  commitment_id: number;
  wallet_address: string;
  tx_hash?: string;
  amount: number;
  unlock_timestamp: number;
  chain_id: number;
  contract_address: string;
  status: "LOCKED" | "UNLOCKED" | "WITHDRAWN";
  commitment_hash: string;
  created_at?: string;
  unlocked_at?: string;
}

export const apiClient = {
  goals: {
    create: async (input: GoalInput): Promise<Commitment> => {
      const response = await api.post("/goals", input);
      return response.data;
    },
  },
  commitments: {
    list: async (): Promise<Commitment[]> => {
      const response = await api.get("/commitments");
      return response.data;
    },
    get: async (id: number): Promise<Commitment> => {
      const response = await api.get(`/commitments/${id}`);
      return response.data;
    },
    getSpending: async (id: number): Promise<Spending[]> => {
      const response = await api.get(`/commitments/${id}/spending`);
      return response.data;
    },
    getDrift: async (id: number): Promise<Drift> => {
      const response = await api.get(`/commitments/${id}/drift`);
      return response.data;
    },
    getInterventions: async (id: number): Promise<Intervention[]> => {
      const response = await api.get(`/commitments/${id}/interventions`);
      return response.data;
    },
    getEvaluation: async (id: number): Promise<Evaluation> => {
      const response = await api.get(`/commitments/${id}/evaluation`);
      return response.data;
    },
    triggerEvaluation: async (id: number): Promise<Evaluation> => {
      const response = await api.post(`/commitments/${id}/evaluate`);
      return response.data;
    },
  },
  spending: {
    add: async (input: SpendingInput): Promise<Spending> => {
      const response = await api.post("/spending", input);
      return response.data;
    },
  },
  interventions: {
    updateOutcome: async (id: number, outcome: string): Promise<void> => {
      await api.patch(`/interventions/${id}/outcome?outcome=${outcome}`);
    },
  },
  escrow: {
    init: async (commitmentId: number): Promise<EscrowInitResponse> => {
      const response = await api.post("/escrow/init", { commitment_id: commitmentId });
      return response.data;
    },
    confirm: async (payload: EscrowConfirmRequest): Promise<{ status: string; escrow_id: number; commitment_id: number }> => {
      const response = await api.post("/escrow/confirm", payload);
      return response.data;
    },
    get: async (commitmentId: number): Promise<EscrowStatus> => {
      const response = await api.get(`/escrow/${commitmentId}`);
      return response.data;
    },
    markWithdrawn: async (commitmentId: number): Promise<void> => {
      await api.patch(`/escrow/${commitmentId}/withdrawn`);
    },
  },
};

export default apiClient;
