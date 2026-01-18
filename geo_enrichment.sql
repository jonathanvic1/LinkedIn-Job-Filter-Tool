-- Add the pp_corrected_name column to geo_candidates
ALTER TABLE geo_candidates ADD COLUMN IF NOT EXISTS pp_corrected_name text;

-- Initialize existing rows
UPDATE geo_candidates SET pp_corrected_name = pp_name WHERE pp_corrected_name IS NULL;
