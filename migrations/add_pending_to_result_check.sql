-- Migration: Add PENDING to match_players result check constraint
-- Date: 2025-11-18
-- Purpose: Allow PENDING result for matches not yet played

-- Drop the old constraint
ALTER TABLE match_players 
DROP CONSTRAINT IF EXISTS match_players_result_check;

-- Add new constraint that includes PENDING
ALTER TABLE match_players 
ADD CONSTRAINT match_players_result_check 
CHECK (result IN ('WIN', 'LOSE', 'PENDING'));
