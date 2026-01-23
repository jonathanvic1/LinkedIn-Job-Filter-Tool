-- New table for user settings
CREATE TABLE IF NOT EXISTS user_settings (
    user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    linkedin_cookie text,
    page_delay float DEFAULT 2.0,
    job_delay float DEFAULT 1.0,
    updated_at timestamptz DEFAULT now()
);

-- Ensure columns exist if table was created before they were added
ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS page_delay float DEFAULT 2.0;
ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS job_delay float DEFAULT 1.0;

-- Index
CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);

-- Enable RLS
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see/edit their own settings
DROP POLICY IF EXISTS user_settings_policy ON user_settings;
CREATE POLICY user_settings_policy ON user_settings
    FOR ALL
    TO authenticated
    USING (user_id = (select auth.uid()))
    WITH CHECK (user_id = (select auth.uid()));
