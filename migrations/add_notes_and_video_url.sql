-- Migration: Add notes and match_video_url to match_reports
-- Date: 2025-11-19
-- Purpose: Allow users to add notes and YouTube link when reporting matches

ALTER TABLE match_reports 
ADD COLUMN notes TEXT,
ADD COLUMN match_video_url VARCHAR(500);
