-- 02: Speed-to-lead — contact rate by minutes from lead creation to first call
WITH first_touch AS (
    SELECT
        lead_id,
        minutes_to_first_call,
        MAX(CASE WHEN outcome = 'connected' THEN 1 ELSE 0 END) AS ever_connected
    FROM calls
    WHERE minutes_to_first_call IS NOT NULL
    GROUP BY 1, 2
)
SELECT
    CASE
        WHEN minutes_to_first_call <= 5 THEN 'under 5 min'
        WHEN minutes_to_first_call <= 30 THEN '5-30 min'
        WHEN minutes_to_first_call <= 60 THEN '30-60 min'
        WHEN minutes_to_first_call <= 240 THEN '1-4 hours'
        ELSE 'over 4 hours'
    END AS speed_bucket,
    COUNT(*) AS leads,
    ROUND(100.0 * SUM(ever_connected) / COUNT(*), 1) AS contact_rate_pct
FROM first_touch
GROUP BY 1
ORDER BY MIN(minutes_to_first_call);
