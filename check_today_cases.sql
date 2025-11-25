SELECT public_id, applicant_name, created_at, status 
FROM cases 
WHERE created_at::date = '2025-11-25' 
ORDER BY created_at DESC;
