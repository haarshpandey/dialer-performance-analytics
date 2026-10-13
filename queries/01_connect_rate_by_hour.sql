-- 01: Connect rate by hour of day — when should reps be dialing?
SELECT
    CAST(strftime('%H', call_at) AS INTEGER) AS hour_of_day,
    COUNT(*) AS dials,
    SUM(CASE WHEN outcome = 'connected' THEN 1 ELSE 0 END) AS connects,
    ROUND(100.0 * SUM(CASE WHEN outcome = 'connected' THEN 1 ELSE 0 END) / COUNT(*), 1) AS connect_rate_pct
FROM calls
GROUP BY 1
ORDER BY 1;
