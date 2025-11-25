SELECT public_id, applicant_name, 
       created_at, 
       created_at AT TIME ZONE 'UTC' as created_utc, 
       created_at AT TIME ZONE 'Europe/Kiev' as created_kiev,
       EXTRACT(timezone FROM created_at) / 3600 as tz_hours
FROM cases 
WHERE public_id = 119179;
