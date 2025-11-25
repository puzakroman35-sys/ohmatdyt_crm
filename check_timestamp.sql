SELECT 
    public_id, 
    created_at, 
    created_at AT TIME ZONE 'UTC' as created_at_utc,
    NOW() as current_time,
    NOW() AT TIME ZONE 'UTC' as current_time_utc
FROM cases 
WHERE public_id = 119179;
