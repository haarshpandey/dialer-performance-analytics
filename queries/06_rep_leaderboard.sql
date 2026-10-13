-- 06: Rep leaderboard — connects, talk time, meetings per 100 dials
SELECT
    r.name,
    r.team,
    COUNT(*) AS dials,
    SUM(CASE WHEN c.outcome = 'connected' THEN 1 ELSE 0 END) AS connects,
    ROUND(100.0 * SUM(CASE WHEN c.outcome = 'connected' THEN 1 ELSE 0 END) / COUNT(*), 1) AS connect_rate_pct,
    ROUND(SUM(c.duration_sec) / 60.0, 0) AS talk_minutes,
    SUM(c.meeting_booked) AS meetings,
    ROUND(100.0 * SUM(c.meeting_booked) / COUNT(*), 1) AS meetings_per_100_dials
FROM calls c
JOIN reps r USING (rep_id)
GROUP BY 1, 2
ORDER BY connect_rate_pct DESC;
