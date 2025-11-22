-- Add tournament_settings table
-- Run this SQL in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS tournament_settings (
    id SERIAL PRIMARY KEY,
    rules TEXT,
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by INTEGER REFERENCES users(user_id)
);

-- Insert default empty record
INSERT INTO tournament_settings (rules, updated_at, updated_by)
VALUES (NULL, NOW(), NULL);

COMMENT ON TABLE tournament_settings IS 'Stores tournament rules and settings';
COMMENT ON COLUMN tournament_settings.rules IS 'HTML content for tournament rules';
COMMENT ON COLUMN tournament_settings.updated_by IS 'User ID of super admin who last updated';
