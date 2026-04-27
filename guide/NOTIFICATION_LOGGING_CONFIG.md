# Notification System Logging Configuration

## Overview

The notification system includes comprehensive logging at multiple levels:

- **INFO**: User actions (connection, disconnection, notification creation)
- **DEBUG**: Detailed execution flow (payload formatting, transaction commits)
- **WARNING**: Issues that don't block execution (anonymous users, missed notifications)
- **ERROR**: Critical failures (channel layer errors, WebSocket push failures)

---

## Django Logging Configuration

Add this to your `settings/development.py` or `settings/production.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {funcName}:{lineno} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {asctime} {name}: {message}',
            'style': '{',
            'datefmt': '%H:%M:%S',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/notifications.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/notifications_error.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'apps.core.services.notification_service': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'apps.core.consumers': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'apps.key.services.notification_service': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'apps.messaging.services.notification_service': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'django.channels': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
```

---

## Log Files Setup

Create the `logs/` directory if it doesn't exist:

```bash
mkdir logs
```

This will create:

- `logs/notifications.log` - All INFO+ level logs from notification services
- `logs/notifications_error.log` - ERROR level logs only

---

## Log Output Examples

### INFO Level (Normal Operations)

```
[INFO] 2026-04-24 10:30:45 apps.core.services.notification_service: Creating notification for user 123: type=API_KEY_CREATED, title=API key generated
[INFO] 2026-04-24 10:30:45 apps.core.services.notification_service: Notification a1b2c3d4 saved to database
[INFO] 2026-04-24 10:30:45 apps.key.services.notification_service: API key 456 created for user 123 (route: Email Form, env: test)
[INFO] 2026-04-24 10:30:46 apps.core.services.notification_service: Successfully pushed notification a1b2c3d4 (API_KEY_CREATED) to group notify_123
[INFO] 2026-04-24 10:30:46 apps.core.consumers: User 123 (user@example.com) connected to notify_123
```

### DEBUG Level (Development Only)

```
[DEBUG] 2026-04-24 10:30:45 apps.core.services.notification_service: Formatted notification payload for a1b2c3d4: {'id': 'a1b2c3d4', 'type': 'API_KEY_CREATED', ...}
[DEBUG] 2026-04-24 10:30:45 apps.core.services.notification_service: Scheduled WebSocket push for notification a1b2c3d4 on transaction commit
[DEBUG] 2026-04-24 10:30:46 apps.core.consumers: WebSocket connection accepted and group added for notify_123
[DEBUG] 2026-04-24 10:30:46 apps.core.consumers: Notification sent successfully to WebSocket for notify_123
```

### WARNING Level (Non-Critical Issues)

```
[WARNING] 2026-04-24 10:30:45 apps.core.consumers: Anonymous user attempted WebSocket connection on notify_test_group
[WARNING] 2026-04-24 10:30:46 apps.core.services.notification_service: WebSocket push failed (non-blocking) for user 123, notification a1b2c3d4: Connection refused
[WARNING] 2026-04-24 10:30:47 apps.messaging.services.notification_service: Message 789 sent but route/user not found. Skipping notification.
```

### ERROR Level (Critical Failures)

```
[ERROR] 2026-04-24 10:30:45 apps.core.services.notification_service: Channel layer is not configured. Cannot push notification a1b2c3d4 to user 123
[ERROR] 2026-04-24 10:30:46 apps.core.services.notification_service: Failed to push notification a1b2c3d4 to group notify_123: [Errno 111] Connection refused
[ERROR] 2026-04-24 10:30:47 apps.messaging.services.notification_service: Message 789 delivery failed for user 123 (route: Email Form, reason: SMTP connection timeout)
```

---

## Monitoring Commands

### Live Tail (Console Only)

```bash
# Watch logs in real-time
tail -f logs/notifications.log

# Follow errors only
tail -f logs/notifications_error.log
```

### Parse Logs by Level

```bash
# Show only INFO logs
grep '\[INFO\]' logs/notifications.log

# Show ERROR and WARNING logs
grep -E '\[ERROR\]|\[WARNING\]' logs/notifications.log

# Show logs for a specific user
grep 'user_id_123' logs/notifications.log
```

### Count Log Messages

```bash
# Count notifications created
grep 'Creating notification' logs/notifications.log | wc -l

# Count WebSocket connections
grep 'connected to' logs/notifications.log | wc -l

# Count failures
grep '\[ERROR\]' logs/notifications_error.log | wc -l
```

---

## Development vs Production

### Development (`DEBUG=True`)

- Console output: **DEBUG** and above
- File output: **INFO** and above
- Fast iteration, see everything
- Use: `python manage.py runserver` or `daphne`

### Production (`DEBUG=False`)

- Console output: **INFO** and above
- File output: **INFO** and above
- More verbose filtering
- Errors are logged separately
- Use: `gunicorn` or `daphne` with supervisor/systemd

---

## Structured Logging (Optional Enhancement)

For production, consider using structured logging with JSON:

```python
# Install: pip install python-json-logger

LOGGING = {
    'handlers': {
        'json_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/notifications.json',
            'formatter': 'json',
        },
    },
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
}
```

This outputs:

```json
{
  "asctime": "2026-04-24 10:30:45",
  "name": "apps.core.services.notification_service",
  "levelname": "INFO",
  "message": "Creating notification for user 123..."
}
```

Benefits:

- Easy to parse with log aggregation tools (ELK, Splunk, etc.)
- Filter and search logs by field
- Better for production monitoring

---

## Debugging Tips

### Issue: Notifications Not Being Sent

1. **Check logs for creation**:

   ```bash
   grep 'Creating notification' logs/notifications.log
   ```

2. **Check WebSocket connection**:

   ```bash
   grep 'connected to' logs/notifications.log
   ```

3. **Check push attempts**:

   ```bash
   grep 'push' logs/notifications.log
   ```

4. **Look for errors**:
   ```bash
   cat logs/notifications_error.log
   ```

### Issue: High Latency

1. **Check transaction commits**:

   ```bash
   grep 'transaction commit' logs/notifications.log
   ```

2. **Look for channel layer issues**:

   ```bash
   grep 'Channel layer' logs/notifications_error.log
   ```

3. **Check for WebSocket delays**:
   ```bash
   grep 'sent successfully' logs/notifications.log
   ```

### Issue: Connection Drops

1. **Check disconnections**:

   ```bash
   grep 'disconnected from' logs/notifications.log
   ```

2. **Check for errors around disconnect time**:
   ```bash
   grep -A5 -B5 'disconnect' logs/notifications.log
   ```

---

## Log Retention Policy

### Automatic Rotation

The `RotatingFileHandler` automatically handles log rotation:

- **Size**: When a log file reaches 10 MB
- **Backups**: Keeps 5 previous backup files
- **Total**: ~60 MB max disk usage per log type

### Manual Cleanup

```bash
# Archive old logs
tar -czf logs/notifications.2024.tar.gz logs/notifications.log.*

# Delete logs older than 30 days
find logs/ -name '*.log*' -mtime +30 -delete
```

---

## Real-Time Monitoring Dashboard

For production, integrate with your monitoring stack:

```python
# Example: Send logs to external service (Sentry, DataDog, etc.)
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    traces_sample_rate=1.0,
)

# Now all ERROR level logs and exceptions are sent to Sentry
```

---

## Performance Considerations

- **Logging overhead**: ~1-2ms per notification log entry
- **Disk I/O**: Minimal with rotating file handler
- **Memory**: Rotating handler keeps only current handle in memory
- **In production**: Use asynchronous handlers for high-traffic scenarios

```python
# Async handler for production (optional):
from logging.handlers import QueueHandler, QueueListener
import queue

# Create queue
log_queue = queue.Queue()

# Async handler
handlers = {
    'async_file': {
        '()': 'logging.handlers.QueueHandler',
        'queue': log_queue,
    },
}

# Start listener in background
listener = QueueListener(log_queue, rotating_file_handler, respect_handler_level=True)
listener.start()
```
