# Frontend WebSocket Notification Implementation Guide

## Quick Start: WebSocket Connection

The backend is ready to send real-time notifications via WebSocket at:

```
ws://localhost:8000/ws/notifications/
```

---

## ✅ Frontend Implementation Checklist

### Phase 1: Basic WebSocket Setup

- [ ] **Install dependencies**
  - [ ] No external dependencies required (native WebSocket API in browsers)
  <!-- - [ ] Optional: Install `socket.io-client` if you want fallback support for older browsers -->

- [ ] **Create notification context/store**
  - [ ] Initialize WebSocket connection manager
  - [ ] Store notifications in state/store
  - [ ] Create handlers for connection events (connect, disconnect, reconnect)

- [ ] **WebSocket connection lifecycle**
  - [ ] Establish connection on component mount / app load
  - [ ] Get JWT token from localStorage or cookies
  - [ ] Pass token in WebSocket URL or custom headers
  - [ ] Handle connection errors gracefully
  - [ ] Implement reconnection logic with exponential backoff

### Phase 2: Message Handling

- [ ] **Receive and parse notifications**
  - [ ] Listen for `message` event on WebSocket
  - [ ] Parse incoming JSON payload
  - [ ] Extract: `id`, `type`, `title`, `message`, `is_read`, `created_at`, `target_id`, `target_type`

- [ ] **Route notifications by type**
  - [ ] `ROUTE_CREATED` - Route management
  - [ ] `ROUTE_UPDATED` - Route management
  - [ ] `API_KEY_CREATED` - Settings/API Keys
  - [ ] `API_KEY_REGENERATED` - Settings/API Keys
  - [ ] `API_KEY_REVOKED` - Settings/API Keys
  - [ ] `MESSAGE_SENT` - Message history
  - [ ] `MESSAGE_FAILED` - Message history / alerts

### Phase 3: UI/UX Features

- [ ] **Display notifications**
  - [ ] Show toast/snackbar for real-time alerts
  - [ ] Update notification bell badge with unread count
  - [ ] Add notification to notification center
  - [ ] Display target link (route, API key, message) if available

- [ ] **User interactions**
  - [ ] Mark notification as read (GET `/api/v2/notifications/{id}/`)
  - [ ] Fetch all notifications with pagination (GET `/api/v2/notifications/`)
  - [ ] Show unread count badge
  - [ ] Archive/delete old notifications

- [ ] **Error handling**
  - [ ] Log connection errors
  - [ ] Show offline indicator when disconnected
  - [ ] Auto-reconnect on network recovery
  - [ ] Fallback: Fetch notifications via REST API if WebSocket fails

### Phase 4: Optimization & Performance

- [ ] **Connection management**
  - [ ] Close WebSocket on logout
  - [ ] Reconnect on login
  - [ ] Debounce rapid reconnection attempts
  - [ ] Graceful degradation without WebSocket

- [ ] **State management**
  - [ ] Prevent duplicate notifications (check by `id`)
  - [ ] Maintain notification history in store
  - [ ] Clear state on logout

- [ ] **Monitoring**
  - [ ] Log WebSocket connection state changes
  - [ ] Track notification delivery latency
  - [ ] Monitor memory usage with large notification lists

---

## 🔄 Sync vs Async on Frontend

### Answer: **You can use both!**

#### **When to use REST (Sync Pattern)**

```javascript
// Get notifications on page load or user action
async function fetchNotifications() {
  const response = await fetch("/api/v2/notifications/");
  const data = await response.json();
  return data.results;
}
```

**Use Cases:**

- Initial page load
- Pagination (load more)
- Mark notification as read
- Refresh after connection loss
- Fallback if WebSocket unavailable

#### **When to use WebSocket (Async/Reactive)**

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/notifications/");

ws.onmessage = (event) => {
  const { notification } = JSON.parse(event.data);
  addNotificationToStore(notification);
  showToast(notification.title);
};
```

**Use Cases:**

- Real-time delivery of new notifications
- Live updates while user is active
- Instant alerts without polling
- Background updates

#### **Recommended Hybrid Approach**

```javascript
// 1. Connect WebSocket on page load
connectWebSocket();

// 2. Fetch existing notifications from API
const existingNotifications = await fetchNotifications();

// 3. New notifications arrive via WebSocket
// 4. If WebSocket disconnects, use REST polling as fallback
// 5. On reconnect, refresh from API to catch missed notifications
```

---

## 📦 Payload Structure

Every notification received via WebSocket has this structure:

```json
{
  "type": "notification",
  "notification": {
    "id": "uuid-string",
    "type": "API_KEY_CREATED",
    "title": "API key generated",
    "message": "A new test API key was created for your route 'Email Form'.",
    "is_read": false,
    "created_at": "2026-04-24T10:30:45.123456Z",
    "target_id": "route-or-api-key-id",
    "target_type": "apikey" // or "route", "message", etc.
  }
}
```

---

## 🚀 Example Implementation (React)

### 1. WebSocket Hook

```javascript
import { useEffect, useRef, useState } from "react";

function useNotificationSocket(token) {
  const [connected, setConnected] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    if (!token) return;

    // Connect to WebSocket
    const ws = new WebSocket(
      `ws://localhost:8000/ws/notifications/?token=${token}`,
    );

    ws.onopen = () => {
      console.log("[WS] Connected");
      setConnected(true);
    };

    ws.onmessage = (event) => {
      const { notification } = JSON.parse(event.data);
      console.log("[WS] Received notification:", notification);

      setNotifications((prev) => [notification, ...prev]);
      // Show toast notification
      showToast(notification.title, notification.message);
    };

    ws.onerror = (error) => {
      console.error("[WS] Error:", error);
      setConnected(false);
    };

    ws.onclose = () => {
      console.log("[WS] Disconnected");
      setConnected(false);
    };

    wsRef.current = ws;

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [token]);

  return { connected, notifications };
}
```

### 2. Notification Center Component

```javascript
function NotificationCenter() {
  const [notifications, setNotifications] = useState([]);
  const { connected } = useNotificationSocket(token);

  // Mark as read
  const markAsRead = async (notificationId) => {
    await fetch(`/api/v2/notifications/${notificationId}/`);
    setNotifications((prev) =>
      prev.map((n) => (n.id === notificationId ? { ...n, is_read: true } : n)),
    );
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <div className="notification-center">
      <div className="header">
        <h2>Notifications</h2>
        {!connected && <span className="offline-badge">Offline</span>}
        {unreadCount > 0 && <span className="badge">{unreadCount}</span>}
      </div>

      <div className="list">
        {notifications.map((notif) => (
          <div
            key={notif.id}
            className={`notification ${notif.is_read ? "read" : "unread"}`}
          >
            <h3>{notif.title}</h3>
            <p>{notif.message}</p>
            <small>{new Date(notif.created_at).toLocaleString()}</small>
            {!notif.is_read && (
              <button onClick={() => markAsRead(notif.id)}>Mark as read</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 3. Toast Notification Helper

```javascript
function showToast(title, message) {
  // Use your favorite toast library (react-hot-toast, react-toastify, etc.)
  // Example with custom implementation:

  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `<strong>${title}</strong><p>${message}</p>`;
  document.body.appendChild(toast);

  setTimeout(() => toast.remove(), 5000);
}
```

---

## 🔐 Authentication

### Option 1: Token in URL (Simple)

```javascript
const token = localStorage.getItem("access_token");
const ws = new WebSocket(
  `ws://localhost:8000/ws/notifications/?token=${token}`,
);
```

### Option 2: Custom Header (Secure)

```javascript
// You may need to configure Django Channels to accept custom headers
const ws = new WebSocket("ws://localhost:8000/ws/notifications/");
// Set header if needed (WebSocket doesn't support custom headers directly)
// Django Channels uses the user from `scope['user']` via AuthMiddlewareStack
```

> **Note**: Django Channels uses `AuthMiddlewareStack` which automatically extracts the user from the WebSocket scope if authenticated via session or JWT middleware.

---

## 📋 Backend Logging for Debugging

Backend logs are written to your Django logger. Check logs for:

```
[INFO] User 123 (user@example.com) connected to notify_123
[INFO] API key 456 created for user 123 (route: Email Form, env: test)
[INFO] Successfully pushed notification abc (API_KEY_CREATED) to group notify_123
[DEBUG] Notification abc sent successfully to WebSocket for notify_123
```

Monitor via:

```bash
# If using file logging:
tail -f logs/django.log

# If using console (development):
python manage.py runserver  # or daphne -b 0.0.0.0 -p 8000 base.asgi:application
```

---

## ⚠️ Common Issues & Fixes

| Issue                        | Cause                         | Solution                                                  |
| ---------------------------- | ----------------------------- | --------------------------------------------------------- |
| WebSocket connection refused | ASGI not running              | Use `daphne` or `uvicorn` instead of `runserver`          |
| Authentication fails         | Token invalid or missing      | Ensure JWT token is valid and passed in URL/cookies       |
| No notifications received    | Channel layer not configured  | Set `REDIS_URL` or use in-memory channel layer (dev only) |
| Notifications delayed        | Connection lag                | Normal; logs show latency if needed                       |
| Lost messages on disconnect  | WebSocket closed unexpectedly | Implement reconnection logic + REST fallback              |

---

## 📚 Related Endpoints

| Endpoint                                | Method | Purpose                                |
| --------------------------------------- | ------ | -------------------------------------- |
| `/api/v2/notifications/`                | GET    | List all notifications (paginated)     |
| `/api/v2/notifications/{id}/read`       | GET    | Get single notification + mark as read |
| `ws://localhost:8000/ws/notifications/` | WS     | Real-time notification stream          |

---

## 🔗 Next Steps

1. Choose your frontend framework (React, Vue, Angular, etc.)
2. Implement the WebSocket hook/service
3. Create notification UI components
4. Test with backend notifications (create an API key, route, etc.)
5. Set up proper error handling and reconnection logic
6. Monitor logs for issues
7. Deploy with `daphne` or `uvicorn` for production WebSocket support
