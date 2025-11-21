# Database Maintenance Runbook

Regular maintenance procedures and troubleshooting for production databases.

## Weekly Maintenance Tasks

### Every Monday 2 AM UTC
Run automated maintenance jobs:

1. **Vacuum Analysis**
   ```sql
   VACUUM ANALYZE;
   ```
   This reclaims storage and updates query planner statistics.

2. **Index Health Check**
   ```sql
   SELECT schemaname, tablename, indexname, idx_scan
   FROM pg_stat_user_indexes
   WHERE idx_scan = 0
   ORDER BY idx_scan;
   ```
   Identifies unused indexes that could be removed.

3. **Slow Query Review**
   - Check `pg_stat_statements` for queries > 1 second
   - Optimize or add indexes as needed

4. **Backup Verification**
   - Verify last night's backup completed successfully
   - Test restore to staging environment (first Monday of month)

## Connection Pool Management

### Checking Current Connections
```sql
SELECT count(*) as connection_count,
       state,
       application_name
FROM pg_stat_activity
WHERE datname = 'production'
GROUP BY state, application_name;
```

### Maximum Connections Alert
If connections exceed 80% of `max_connections`:

1. Identify problematic applications:
   ```sql
   SELECT application_name, count(*) 
   FROM pg_stat_activity 
   GROUP BY application_name 
   ORDER BY count DESC;
   ```

2. Check for connection leaks in application logs
3. Consider increasing pool size or max_connections
4. Restart application servers if necessary

## Performance Troubleshooting

### High CPU Usage

1. Identify expensive queries:
   ```sql
   SELECT query, calls, total_time, mean_time
   FROM pg_stat_statements
   ORDER BY total_time DESC
   LIMIT 10;
   ```

2. Check for missing indexes on frequently queried columns
3. Review EXPLAIN ANALYZE output for slow queries
4. Consider query rewrite or application-level caching

### High Disk I/O

1. Check for large table scans:
   ```sql
   SELECT schemaname, tablename, seq_scan, seq_tup_read
   FROM pg_stat_user_tables
   WHERE seq_scan > 1000
   ORDER BY seq_tup_read DESC;
   ```

2. Add indexes to reduce sequential scans
3. Consider table partitioning for very large tables

### Replication Lag

Check replication status:
```sql
SELECT client_addr,
       state,
       sent_lsn,
       write_lsn,
       flush_lsn,
       replay_lsn,
       sync_state
FROM pg_stat_replication;
```

If lag > 100MB:
1. Check replica server resources (CPU, disk I/O)
2. Verify network connectivity
3. Check for long-running transactions on replica
4. Consider increasing `max_wal_senders` and `wal_keep_segments`

## Backup and Restore

### Manual Backup
```bash
pg_dump -h prod-db.company.com -U backup_user -Fc production > backup_$(date +%Y%m%d).dump
```

### Restore to Staging
```bash
pg_restore -h staging-db.company.com -U admin -d staging --clean backup_20250101.dump
```

### Point-in-Time Recovery
For disaster recovery, follow the PITR guide in the disaster recovery documentation.

## Monitoring Alerts

### Critical Alerts (Page On-Call)
- Database down or unreachable
- Replication stopped
- Disk usage > 90%
- Connection pool exhausted

### Warning Alerts (Slack Notification)
- Slow query detected (> 5 seconds)
- Replication lag > 50MB
- Disk usage > 75%
- Unusual connection count

## Emergency Procedures

### Database Not Accepting Connections
1. Check if PostgreSQL service is running: `systemctl status postgresql`
2. Check system resources (disk space, memory)
3. Review PostgreSQL logs: `/var/log/postgresql/postgresql-*.log`
4. If disk full, clear old logs or WAL files (carefully!)
5. Restart PostgreSQL service if necessary

### Data Corruption Detected
1. Immediately stop all write operations
2. Create emergency backup of current state
3. Engage Database Administrator and VP Engineering
4. Do NOT attempt repairs without DBA guidance
5. Restore from latest known-good backup if needed

!!! danger "Production Database Access"
    Only authorized DBAs should perform write operations on production databases. Always test maintenance procedures in staging first.

