-- 03: Spam-flag impact — connect rate on clean vs spam-likely numbers
SELECT
    CASE WHEN l.phone_flagged = 1 THEN 'flagged (spam-likely)' ELSE 'clean' END AS number_status,
    COUNT(*) AS dials,
    ROUND(100.0 * SUM(CASE WHEN c.outcome = 'connected' THEN 1 ELSE 0 END) / COUNT(*), 1) AS connect_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN c.outcome = 'failed' THEN 1 ELSE 0 END) / COUNT(*), 1) AS failed_rate_pct
FROM calls c
JOIN leads l USING (lead_id)
GROUP BY 1;
