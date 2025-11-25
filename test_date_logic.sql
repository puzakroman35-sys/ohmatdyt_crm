-- Test 1: Check case exists on 2025-11-25
SELECT public_id, applicant_name, created_at, status 
FROM cases 
WHERE created_at::date = '2025-11-25';

-- Test 2: Check with exact timestamp range (00:00:00)
SELECT public_id, applicant_name, created_at 
FROM cases 
WHERE created_at >= '2025-11-25 00:00:00'::timestamp 
  AND created_at <= '2025-11-25 00:00:00'::timestamp;

-- Test 3: Check with end of day (23:59:59)
SELECT public_id, applicant_name, created_at 
FROM cases 
WHERE created_at >= '2025-11-25 00:00:00'::timestamp 
  AND created_at <= '2025-11-25 23:59:59.999999'::timestamp;
