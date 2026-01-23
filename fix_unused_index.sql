-- Remove the unused B-Tree index that is causing the performance warning.
-- Standard B-Tree indexes don't work with array containment queries like .contains() in PostgREST.

DROP INDEX IF EXISTS idx_geo_candidates_master_geo_id;

-- OPTIONAL: If your geo_candidates table grows very large (thousands of rows),
-- uncomment the line below to create a GIN index, which IS optimized for arrays.
-- CREATE INDEX idx_geo_candidates_master_geo_id_gin ON geo_candidates USING GIN (master_geo_id);
