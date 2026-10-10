WITH tracked AS (
    SELECT timestamp, distinct_id, properties.visit_id AS visit_id
    FROM events
    WHERE event IN ('$pageview', '$pageleave', 'photo_open', 'details_open',
                    'gallery_open', 'engagement', 'outbound_click')
), bounds AS (
    SELECT
        toDate(toTimeZone(now(), 'America/New_York')) AS today,
        min(toDate(toTimeZone(timestamp, 'America/New_York'))) AS first_day
    FROM tracked
    WHERE timestamp < now()
    HAVING count() > 0
), days AS (
    SELECT today - toIntervalDay(arrayJoin(range(1, 29))) AS day
    FROM bounds
    WHERE day > first_day
), daily AS (
    SELECT
        toDate(toTimeZone(timestamp, 'America/New_York')) AS day,
        toHour(toTimeZone(timestamp, 'America/New_York')) AS hour,
        count(DISTINCT distinct_id) AS browsers,
        count(DISTINCT visit_id) AS visits
    FROM tracked
    WHERE timestamp >= toDateTime(
        toString(toDate(toTimeZone(now(), 'America/New_York')) - INTERVAL 28 DAY),
        'America/New_York')
        AND timestamp < toDateTime(
            toString(toDate(toTimeZone(now(), 'America/New_York'))), 'America/New_York')
    GROUP BY day, hour
)
SELECT
    leftPad(toString(hours.hour), 2, '0') AS eastern_hour,
    round(avg(coalesce(daily.browsers, 0)), 1) AS avg_browsers,
    round(avg(coalesce(daily.visits, 0)), 1) AS avg_visits,
    count() AS complete_days
FROM days
CROSS JOIN (SELECT arrayJoin(range(0, 24)) AS hour) AS hours
LEFT JOIN daily ON daily.day = days.day AND daily.hour = hours.hour
GROUP BY hours.hour
ORDER BY hours.hour
