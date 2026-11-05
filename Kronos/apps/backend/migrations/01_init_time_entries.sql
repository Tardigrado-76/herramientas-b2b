-- Create enum for entry types
DO $$ BEGIN
    CREATE TYPE entry_type AS ENUM ('IN', 'OUT', 'PAUSE_IN', 'PAUSE_OUT');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create time_entries table
CREATE TABLE IF NOT EXISTS time_entries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
    type entry_type NOT NULL,
    location GEOGRAPHY(POINT, 4326),
    device_info JSONB,
    ip_address TEXT,
    recorded_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Add constraint to ensure recorded_at is reasonable
    CONSTRAINT reasonable_date CHECK (recorded_at > '2025-01-01'::timestamptz)
);

-- Create index for faster queries by user and date
CREATE INDEX IF NOT EXISTS idx_time_entries_user_date ON time_entries (user_id, recorded_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE time_entries ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own entries
CREATE POLICY "Users can view own entries" ON time_entries
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can only insert their own entries
CREATE POLICY "Users can insert own entries" ON time_entries
    FOR INSERT WITH CHECK (auth.uid() = user_id);
