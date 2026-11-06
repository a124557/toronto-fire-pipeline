-- One SQL transform layer on top of the raw ingest.
CREATE OR REPLACE TABLE fire_incidents_by_ward_month AS
SELECT
  COALESCE(NULLIF(TRIM(incident_ward), ''), 'UNKNOWN') AS ward,
  date_trunc('month', tfs_alarm_time) AS alarm_month,
  COUNT(*) AS incident_count,
  COUNT(DISTINCT final_incident_type) AS distinct_incident_types,
  AVG(
    CASE
      WHEN tfs_arrival_time IS NOT NULL AND tfs_alarm_time IS NOT NULL
        THEN date_diff('second', tfs_alarm_time, tfs_arrival_time)
    END
  ) AS avg_response_seconds
FROM raw_fire_incidents
WHERE tfs_alarm_time IS NOT NULL
GROUP BY 1, 2
ORDER BY alarm_month DESC, incident_count DESC;

CREATE OR REPLACE TABLE fire_incidents_top_types AS
SELECT
  COALESCE(NULLIF(TRIM(final_incident_type), ''), 'UNKNOWN') AS final_incident_type,
  COUNT(*) AS incident_count
FROM raw_fire_incidents
GROUP BY 1
ORDER BY incident_count DESC
LIMIT 25;
