SELECT
    if(toString(properties.destination) IN (
        'brokerage-phone', 'agent-email', 'other-phone', 'other-email',
        'brokerage-listing', 'zillow', 'redfin', 'other-external'
    ), toString(properties.destination), 'unknown') AS destination,
    if(toString(properties.placement) IN ('header', 'contact', 'content', 'footer'),
        toString(properties.placement), 'unknown') AS placement,
    count() AS clicks,
    count(DISTINCT properties.visit_id) AS visits,
    count(DISTINCT distinct_id) AS browsers
FROM events
WHERE timestamp >= now() - INTERVAL 28 DAY
    AND timestamp < now()
    AND event = 'outbound_click'
GROUP BY destination, placement
ORDER BY clicks DESC, destination, placement
