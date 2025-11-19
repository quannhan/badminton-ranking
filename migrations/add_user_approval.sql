-- Migration: Add is_active column to users table
-- Date: 2025-11-18
-- Description: Add account approval system - users need admin approval to login

-- Add is_active column (default FALSE for new users)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT FALSE;

-- Set existing users to active (so they can continue logging in)
UPDATE users 
SET is_active = TRUE 
WHERE is_active IS NULL OR is_active = FALSE;

-- Create index for faster queries on pending users
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Show stats
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN is_active = TRUE THEN 1 ELSE 0 END) as active_users,
    SUM(CASE WHEN is_active = FALSE THEN 1 ELSE 0 END) as pending_users
FROM users;
