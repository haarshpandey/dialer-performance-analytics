-- 04: Multi-line efficiency — does dialing 3 lines at once pay off?
SELECT
    lines_used,
    COUNT(*) AS dials,
    ROUND(100.0 * SUM(CASE WHEN outcome = 'connected' THEN 1 ELSE 0 END) / COUNT(*), 1) AS connect_rate_pct,
    ROUND(AVG(duration_sec), 0) AS avg_duration_sec,
    ROUND(100.0 * SUM(meeting_booked) / NULLIF(SUM(CASE WHEN outcome = 'connected' THEN 1 ELSE 0 END), 0), 1) AS meeting_rate_pct
FROM calls
GROUP BY 1
ORDER BY 1;
