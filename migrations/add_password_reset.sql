-- Create user_settings table instead of adding column to users
CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    require_password_change BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create password_reset_requests table
CREATE TABLE IF NOT EXISTS password_reset_requests (
    request_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    email VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'PENDING',
    new_password VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    resolved_by INTEGER REFERENCES users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_password_reset_status ON password_reset_requests(status);
CREATE INDEX IF NOT EXISTS idx_password_reset_user ON password_reset_requests(user_id);
