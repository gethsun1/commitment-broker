-- Migration: Add new AI evaluation fields to evaluations table
-- Run this migration to add the new columns for AI-generated evaluation metrics

-- Add evaluation_snapshot column (JSON)
ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS evaluation_snapshot JSON;

-- Add behavioral_recovery_score column (Integer, 0-100)
ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS behavioral_recovery_score INTEGER;

-- Add behavioral_recovery_interpretation column (Text)
ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS behavioral_recovery_interpretation TEXT;

-- Add adherence_trend column (String)
ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS adherence_trend VARCHAR(50);

-- Add adherence_confidence column (Float)
ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS adherence_confidence FLOAT;

-- Add intervention_justification column (Text)
ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS intervention_justification TEXT;

-- Add drift_classification_confidence column (Float)
ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS drift_classification_confidence FLOAT;

-- Add planning_accuracy column (Float)
ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS planning_accuracy FLOAT;

-- Add drift_detection_precision column (Float)
ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS drift_detection_precision FLOAT;

-- Add intervention_timing column (String)
ALTER TABLE evaluations 
ADD COLUMN IF NOT EXISTS intervention_timing VARCHAR(50);
