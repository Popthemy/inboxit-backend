# Notification System - Quick Reference Card

## 🚀 Backend Quick Start

### Running the Server (WebSocket Ready)

```bash
# Development (with hot reload)
daphne -b 0.0.0.0 -p 8000 base.asgi:application

# Production
daphne -b 0.0.0.0 -p 8000 -u /run/daphne.sock base.asgi:application
```

### Checking Notifications Work

```bash
# Create an API key (sends API_KEY_CREATED notification)
curl -X POST http://localhost:8000/api/v2/keys/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"route": 123, "env_choice": "test"}'

# Create a route (sends ROUTE_CREATED notification)
curl -X POST http://localhost:8000/api/v2/routes/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"channel": "email", "label": "Test Route", "recipient_emails": "test@example.com"}'
```

---

## 📝 Logging Quick Commands

### View Real-Time Logs

```bash
# All notifications
tail -f logs/notifications.log

# Errors only
tail -f logs/notifications_error.log

# Follow both
tail -f logs/notifications*.log
```

### Search Logs

```bash
# All INFO logs
grep '\[INFO\]' logs/notifications.log

# Errors and warnings
grep -E '\[ERROR\]|\[WARNING\]' logs/notifications.log

# Specific user activity
grep 'user_id' logs/notifications.log

# Failed pushes
grep 'failed' logs/notifications.log
```

---

## 🎯 Frontend Quick Setup (React)

### 1. Install Dependencies

```bash
npm install  # No additional packages needed for basic WebSocket
# Optional: npm install react-hot-toast  (for toast notifications)
```

### 2. Create Hook

```javascript
import { useEffect, useState } from "react";

function useNotifications(token) {
  const [notifications, setNotifications] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(
      `ws://localhost:8000/ws/notifications/?token=${token}`,
    );

    ws.onopen = () => setConnected(true);
    ws.onmessage = (e) => {
      const { notification } = JSON.parse(e.data);
      setNotifications((prev) => [notification, ...prev]);
    };
    ws.onclose = () => setConnected(false);

    return () => ws.close();
  }, [token]);

  return { notifications, connected };
}
```

### 3. Use in Component

```javascript
function NotificationBell() {
  const { notifications, connected } = useNotifications(token);
  const unread = notifications.filter((n) => !n.is_read).length;

  return (
    <div>
      <button>
        🔔 {unread > 0 && <span className="badge">{unread}</span>}
      </button>
      {!connected && <span className="offline">Offline</span>}
    </div>
  );
}
```

---

## 📊 Notification Types

| Type                  | Source        | When                    | User Action      |
| --------------------- | ------------- | ----------------------- | ---------------- |
| `API_KEY_CREATED`     | Key app       | New API key issued      | View in settings |
| `API_KEY_REGENERATED` | Key app       | Key regenerated         | Update client    |
| `API_KEY_REVOKED`     | Key app       | Key revoked             | Update client    |
| `ROUTE_CREATED`       | Messaging app | New delivery route      | View in routes   |
| `ROUTE_UPDATED`       | Messaging app | Route settings changed  | Verify settings  |
| `MESSAGE_SENT`        | Messaging app | Message delivered       | View in messages |
| `MESSAGE_FAILED`      | Messaging app | Message delivery failed | Troubleshoot     |

---

## 🔍 API Endpoints

```
GET    /api/v2/notifications/           # List all (paginated)
GET    /api/v2/notifications/{id}/      # Get one + mark read
WS     ws://localhost:8000/ws/notifications/  # Real-time stream
```

---

## ⚠️ Common Issues

| Problem                | Fix                                       |
| ---------------------- | ----------------------------------------- |
| "Connection refused"   | Run with `daphne`, not `runserver`        |
| No WebSocket in logs   | Check `ASGI_APPLICATION` setting          |
| Empty notifications    | Check logs for errors with `grep 'ERROR'` |
| Notifications delayed  | Check Redis/channel layer logs            |
| Frontend can't connect | Verify token is valid, CORS enabled       |

---

## 🧪 Quick Testing Script

```bash
#!/bin/bash

# Test backend notification creation
python manage.py shell << EOF
from apps.core.services.notification_service import NotificationService
from apps.core.models import NotificationType
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

NotificationService.create(
    user=user,
    notification_type=NotificationType.API_KEY_CREATED,
    title="Test Notification",
    message="This is a test notification"
)
print("✓ Notification created. Check logs and WebSocket client.")
EOF
```

---

## 📚 Documentation Files

- **FRONTEND_NOTIFICATION_GUIDE.md** - Complete frontend implementation guide
- **NOTIFICATION_LOGGING_CONFIG.md** - Logging setup and debugging
- This file - Quick reference

---

## 🔗 Key Files & Changes

### Backend Services

- `apps/core/services/notification_service.py` - Core dispatch logic
- `apps/key/services/notification_service.py` - API key notifications
- `apps/messaging/services/notification_service.py` - Route & message notifications

### WebSocket

- `apps/core/consumers.py` - WebSocket consumer with logging
- `base/asgi.py` - ASGI routing configured
- `apps/core/routing.py` - WebSocket URL patterns

### Configuration

- `base/settings/general.py` - Channel layer config
- `requirements.txt` - Added `channels` and `channels-redis`

---

## 📋 Sync vs Async - When to Use

### Use REST (Sync)

- Initial page load
- Pagination
- Mark notification as read
- Fallback if WebSocket unavailable

### Use WebSocket (Async)

- Real-time delivery
- Live updates while user active
- Instant alerts
- Background updates

### Best Practice: Use Both

```javascript
// 1. WebSocket for real-time
ws.onmessage = (e) => addNotification(e.data);

// 2. REST for initial load + fallback
if (!wsConnected) {
  fetchNotificationsFromAPI();
}

// 3. Refresh on reconnect
ws.onopen = () => refreshFromAPI();
```

---

## 🚨 Emergency Commands

### Clear all notifications (dev only)

```bash
python manage.py shell << EOF
from apps.core.models import Notification
Notification.objects.all().delete()
EOF
```

### Check channel layer status

```bash
python manage.py shell << EOF
from channels.layers import get_channel_layer
layer = get_channel_layer()
print(f"Channel layer: {layer}")
print(f"Configured: {layer is not None}")
EOF
```

### Reset Redis cache (if using)

```bash
redis-cli FLUSHDB
```

---

## 📞 Getting Help

1. **Check logs first**: `tail -f logs/notifications*.log`
2. **Search for errors**: `grep 'ERROR' logs/notifications.log`
3. **Frontend not receiving**: Check WebSocket connection in browser DevTools
4. **Backend logs empty**: Make sure logging is configured in settings
