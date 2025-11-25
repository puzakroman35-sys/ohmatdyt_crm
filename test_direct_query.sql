-- Check created_at column type
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'cases' AND column_name = 'created_at';

-- Test direct query
SELECT public_id, created_at
FROM cases
WHERE created_at >= '2025-11-25 00:00:00'
  AND created_at <= '2025-11-25 23:59:59.999999';
