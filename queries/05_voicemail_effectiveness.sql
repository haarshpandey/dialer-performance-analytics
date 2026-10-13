-- 05: Voicemail drops — do pre-recorded voicemails earn a callback connection later?
WITH lead_vm AS (
    SELECT
        lead_id,
        MAX(voicemail_dropped) AS got_drop,
        MAX(CASE WHEN outcome = 'connected' THEN 1 ELSE 0 END) AS ever_connected
    FROM calls
    WHERE outcome IN ('connected', 'voicemail')
    GROUP BY 1
    HAVING SUM(CASE WHEN outcome = 'voicemail' THEN 1 ELSE 0 END) > 0
)
SELECT
    CASE WHEN got_drop = 1 THEN 'voicemail drop left' ELSE 'no drop' END AS group_name,
    COUNT(*) AS leads,
    ROUND(100.0 * SUM(ever_connected) / COUNT(*), 1) AS eventual_contact_pct
FROM lead_vm
GROUP BY 1;
