# Troubleshooting

Comprehensive troubleshooting guide for common issues, error resolution, and debugging tips for the Catalog Portfolio API service.

## Overview

This section provides solutions to common problems you might encounter while working with the Catalog Portfolio API service, from setup issues to runtime errors.

This section provides comprehensive troubleshooting information for common issues and debugging techniques.


  <i class="fas fa-download"></i> Download Troubleshooting Template


## Quick Diagnostic

### Health Check

First, verify the service is running:

```bash
# Check service health
curl http://localhost:8080/catalog/brands/ping
# Expected: "pong"

# Check if port is in use
lsof -i :8080
```

### Database Connection

Verify database connectivity:

```bash
# Test MySQL connection
mysql -h localhost -u your_username -p -e "SELECT 1;"

# Check database exists
mysql -h localhost -u your_username -p -e "SHOW DATABASES LIKE 'brands_%';"
```

### Configuration Check

Verify configuration files:

```bash
# Check if configuration files exist
ls -la src/main/resources/development/
ls -la src/main/resources/production/

# Validate properties format
grep -v '^#' src/main/resources/development/application.properties
```

## Common Error Categories

### 🔧 Startup Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Port Already in Use** | `Address already in use` | Change port or kill existing process |
| **Database Connection Failed** | `Connection refused` | Verify MySQL is running and credentials |
| **Missing Configuration** | `FileNotFoundException` | Ensure all config files are present |
| **Invalid Database Schema** | `Table doesn't exist` | Run database migrations |

### 🌐 API Request Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **404 Not Found** | Brand not found errors | Verify brand ID exists in database |
| **400 Bad Request** | Validation errors | Check request payload format |
| **401 Unauthorized** | Authentication failures | Verify API keys and permissions |
| **422 Unprocessable** | Business logic errors | Check brand activation requirements |

### 🗄️ Database Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Connection Pool Exhausted** | Timeout errors | Increase pool size or fix connection leaks |
| **Slow Queries** | High response times | Add database indexes, optimize queries |
| **Lock Timeouts** | Deadlock errors | Review transaction boundaries |
| **Migration Failures** | Schema inconsistencies | Rollback and rerun migrations |

## Error Code Reference

### HTTP Status Codes

| Code | Error Type | Description | Action Required |
|------|------------|-------------|-----------------|
| `400` | Bad Request | Invalid request format | Fix request payload |
| `401` | Unauthorized | Missing/invalid auth | Check authentication |
| `403` | Forbidden | Insufficient permissions | Verify client permissions |
| `404` | Not Found | Resource doesn't exist | Verify resource ID |
| `409` | Conflict | Resource already exists | Use different name/ID |
| `422` | Unprocessable | Business logic error | Check validation rules |
| `500` | Server Error | Internal error | Check server logs |

### Application Error Codes

| Error Code | Description | Common Causes |
|------------|-------------|---------------|
| `brand_not_found` | Brand ID doesn't exist | Invalid ID, deleted brand |
| `brand_name_already_exists` | Duplicate brand name | Name conflict within site |
| `logos_missing` | Required logos not uploaded | Missing main logo for activation |
| `validation_failed` | Business rules failed | Category issues, invalid data |
| `unauthorized` | Permission denied | Missing client permissions |
| `database_error` | Database operation failed | Connection issues, constraints |

## Debug Strategies

### Logging Configuration

Enable debug logging in `log4j2.xml`:

```xml
<Logger name="com.retailflow.catalog.portfolio" level="DEBUG"/>
<Logger name="com.zaxxer.hikari" level="DEBUG"/>
<Logger name="org.apache.http" level="DEBUG"/>
```

### Database Debugging

```sql
-- Check brand exists
SELECT * FROM brand WHERE id = 123;

-- Verify brand status
SELECT name, status, date_created FROM brand WHERE status = 'STAND_BY';

-- Check logo requirements
SELECT b.name, COUNT(l.id) as logo_count 
FROM brand b 
LEFT JOIN logo l ON b.id = l.brand_id 
WHERE b.id = 123;
```

### API Testing

```bash
# Test with verbose output
curl -v "http://localhost:8080/catalog/brands/123"

# Test with timing
curl -w "@curl-format.txt" "http://localhost:8080/catalog/brands/"

# Test authentication
curl -H "X-Client-Id: test" "http://localhost:8080/catalog/brands/"
```

## Performance Issues

### Slow API Responses

1. **Check Database Performance**:
   ```sql
   SHOW PROCESSLIST;
   EXPLAIN SELECT * FROM brand WHERE name LIKE '%test%';
   ```

2. **Monitor JVM Memory**:
   ```bash
   jstat -gc $PID 5s
   jstack $PID
   ```

3. **Check Connection Pool**:
   ```bash
   # Monitor database connections
   mysql -e "SHOW STATUS LIKE 'Threads_connected';"
   ```

### Memory Issues

```bash
# Check memory usage
free -h
ps aux | grep java

# Monitor heap usage
jstat -heap $PID

# Generate heap dump
jcmd $PID GC.run_finalization
jcmd $PID VM.classloader_stats
```

## Environment-Specific Issues

### Local Development

- **Issue**: Database migrations fail
- **Solution**: Ensure MySQL version compatibility and user permissions

- **Issue**: External API calls fail
- **Solution**: Check network connectivity and API endpoints

### Production Deployment

- **Issue**: Configuration not loading
- **Solution**: Verify environment variables and file permissions

- **Issue**: High memory usage
- **Solution**: Tune JVM parameters and garbage collection

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Response Times**: Average < 100ms
2. **Error Rates**: < 1% for 4xx/5xx errors
3. **Database Connections**: Pool utilization < 80%
4. **Memory Usage**: Heap usage < 85%

## Getting Help

### Log Analysis

When reporting issues, include:

1. **Error messages** from application logs
2. **Request/response** examples
3. **Environment details** (Java version, MySQL version)
4. **Configuration** (sanitized, no passwords)

### Support Channels

- **Email**: [instore_devs@retailflow.com](mailto:instore_devs@retailflow.com)
- **Slack**: #instore-dev
- **Monitoring**: [DataDog Dashboard](https://monitoring.retailflow.io/dashboard/vua-inb-9et?fromUser=false&refresh_mode=sliding&from_ts=1750955519638&to_ts=1750959119638&live=true)

### Escalation Process

1. **Level 1**: Check this troubleshooting guide
2. **Level 2**: Search existing documentation and logs
3. **Level 3**: Contact development team with detailed information
4. **Level 4**: Emergency escalation for production issues 