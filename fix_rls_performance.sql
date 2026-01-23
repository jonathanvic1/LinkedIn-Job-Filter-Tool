-- Optimization: Wrap auth.uid() in a subquery to prevent per-row re-evaluation
-- This significantly improves performance on large tables like dismissed_jobs.

-- 1. user_settings
DROP POLICY IF EXISTS user_settings_policy ON user_settings;
DROP POLICY IF EXISTS "Service role only" ON user_settings;
CREATE POLICY user_settings_policy ON user_settings
    FOR ALL TO authenticated
    USING (user_id = (select auth.uid()))
    WITH CHECK (user_id = (select auth.uid()));

-- 2. dismissed_jobs
DROP POLICY IF EXISTS dismissed_jobs_policy ON dismissed_jobs;
DROP POLICY IF EXISTS "Service role only" ON dismissed_jobs;
DROP POLICY IF EXISTS "Restrict access to dismissed_jobs" ON dismissed_jobs;
CREATE POLICY dismissed_jobs_policy ON dismissed_jobs
    FOR ALL TO authenticated
    USING (user_id = (select auth.uid()))
    WITH CHECK (user_id = (select auth.uid()));

-- 3. blocklists
DROP POLICY IF EXISTS blocklists_policy ON blocklists;
DROP POLICY IF EXISTS "Service role only" ON blocklists;
DROP POLICY IF EXISTS "Blocklists Table" ON blocklists;
CREATE POLICY blocklists_policy ON blocklists
    FOR ALL TO authenticated
    USING (user_id = (select auth.uid()))
    WITH CHECK (user_id = (select auth.uid()));
