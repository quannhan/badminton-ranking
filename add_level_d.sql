-- Add level D support to the system
-- Run this SQL in your Supabase SQL Editor

-- Step 1: Modify the level column constraint if exists
-- (In PostgreSQL, String(1) in SQLAlchemy creates a VARCHAR(1) which already allows 'D')
-- So we just need to update default value for new users if needed

-- Step 2: Update any existing constraints or checks (if any)
-- This is precautionary - adjust based on your actual schema

-- Step 3: Optionally set default to 'D' for new users (or keep 'C')
-- ALTER TABLE users ALTER COLUMN level SET DEFAULT 'D';

-- Note: The database should already support 'D' since it's just a VARCHAR(1) field
-- This migration is mainly for documentation purposes

-- You can now create users with level 'D' without any database changes needed

COMMENT ON COLUMN users.level IS 'User skill level: D (Beginner), C (New), B (Intermediate), A (Advanced)';
