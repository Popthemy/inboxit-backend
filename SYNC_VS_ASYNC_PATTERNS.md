# Sync vs Async Communication Patterns - Frontend Guide

## The Answer: **YES, You Can Use Both!**

The frontend can seamlessly blend synchronous (REST) and asynchronous (WebSocket) patterns. This document explains when and how to use each.

---

## 📋 Pattern Comparison

### REST API (Synchronous)

```javascript
// Request → Wait → Response (blocking)
async function fetchNotifications() {
  const response = await fetch("/api/v2/notifications/");
  const data = await response.json();
  return data.results; // You wait here until response arrives
}
```

**Characteristics:**

- ✅ Guaranteed delivery (HTTP status codes)
- ✅ Request/response model
- ✅ Easy to implement
- ❌ Requires active polling for real-time
- ❌ Higher latency (~100-500ms per request)

**Best for:**

- Initial data load
- User-triggered actions (mark as read)
- Pagination (load more)
- Fallback when WebSocket unavailable
- Admin dashboards (less frequent updates)

---

### WebSocket (Asynchronous)

```javascript
// Server pushes data anytime (non-blocking)
ws.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  addToNotificationList(notification); // Instant delivery
};
```

**Characteristics:**

- ✅ Real-time delivery (~10-50ms latency)
- ✅ Bidirectional communication
- ✅ Low overhead (persistent connection)
- ✅ Server-initiated messages
- ❌ Requires connection management
- ❌ More complex error handling

**Best for:**

- Real-time alerts
- Live updates while user active
- Background notifications
- Dashboard streams
- Collaborative features

---

## 🔄 Hybrid Strategy: Using Both

### The Complete Flow

```javascript
class NotificationManager {
  constructor(token) {
    this.token = token;
    this.notifications = [];
    this.wsConnected = false;
    this.wsRetries = 0;
    this.maxRetries = 5;
  }

  // PHASE 1: Initial Load (REST)
  async initialize() {
    console.log("📥 Loading initial notifications from REST API...");
    try {
      const response = await fetch("/api/v2/notifications/", {
        headers: { Authorization: `Bearer ${this.token}` },
      });
      const data = await response.json();
      this.notifications = data.results || [];
      console.log(`✓ Loaded ${this.notifications.length} notifications`);
    } catch (error) {
      console.error("❌ Failed to load notifications:", error);
      this.notifications = [];
    }

    // PHASE 2: Connect WebSocket (Async)
    this.connectWebSocket();
  }

  // PHASE 2: Real-Time Connection (WebSocket)
  connectWebSocket() {
    console.log("🔌 Connecting to WebSocket...");

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const url = `${protocol}//${window.location.host}/ws/notifications/?token=${this.token}`;

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log("✓ WebSocket connected");
      this.wsConnected = true;
      this.wsRetries = 0;
    };

    // New notifications arrive here (server push)
    this.ws.onmessage = (event) => {
      const { notification } = JSON.parse(event.data);
      console.log("📨 New notification via WebSocket:", notification.title);

      // Avoid duplicates (check by ID)
      if (!this.notifications.find((n) => n.id === notification.id)) {
        this.notifications.unshift(notification);
        this.emitEvent("notification:new", notification);
        this.showToast(notification);
      }
    };

    this.ws.onerror = (error) => {
      console.error("❌ WebSocket error:", error);
      this.wsConnected = false;
    };

    this.ws.onclose = () => {
      console.log("⚠️ WebSocket disconnected");
      this.wsConnected = false;

      // PHASE 3: Fallback & Reconnect Logic
      this.reconnectWithBackoff();
    };
  }

  // PHASE 3: Reconnection with Exponential Backoff
  reconnectWithBackoff() {
    if (this.wsRetries >= this.maxRetries) {
      console.error(
        "❌ Max reconnection attempts reached. Using REST polling fallback.",
      );
      this.startRestPolling();
      return;
    }

    const delay = Math.min(1000 * Math.pow(2, this.wsRetries), 30000);
    this.wsRetries++;

    console.log(`🔄 Reconnecting in ${delay}ms... (attempt ${this.wsRetries})`);
    setTimeout(() => this.connectWebSocket(), delay);
  }

  // PHASE 4: REST Polling Fallback (if WebSocket fails)
  startRestPolling() {
    console.log(
      "📡 WebSocket failed. Switching to REST polling every 5 seconds...",
    );

    this.pollInterval = setInterval(async () => {
      try {
        const response = await fetch("/api/v2/notifications/", {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        const data = await response.json();
        const newNotifications = data.results || [];

        // Check for new notifications
        newNotifications.forEach((notif) => {
          if (!this.notifications.find((n) => n.id === notif.id)) {
            console.log("📨 New notification via REST polling:", notif.title);
            this.notifications.unshift(notif);
            this.emitEvent("notification:new", notif);
            this.showToast(notif);
          }
        });

        // If WebSocket comes back, stop polling
        if (this.wsConnected) {
          console.log("✓ WebSocket reconnected. Stopping REST polling.");
          clearInterval(this.pollInterval);
        }
      } catch (error) {
        console.warn("⚠️ REST polling error:", error);
      }
    }, 5000);
  }

  // PHASE 5: Mark as Read (REST - User Action)
  async markAsRead(notificationId) {
    console.log(`📖 Marking notification ${notificationId} as read...`);

    try {
      const response = await fetch(`/api/v2/notifications/${notificationId}/`, {
        method: "GET",
        headers: { Authorization: `Bearer ${this.token}` },
      });

      if (response.ok) {
        // Update local state
        const notif = this.notifications.find((n) => n.id === notificationId);
        if (notif) notif.is_read = true;

        this.emitEvent("notification:read", notificationId);
        console.log("✓ Marked as read");
      }
    } catch (error) {
      console.error("❌ Failed to mark as read:", error);
    }
  }

  // PHASE 6: Refresh on Reconnect
  async refreshNotifications() {
    console.log("🔄 Refreshing notifications...");

    try {
      const response = await fetch("/api/v2/notifications/", {
        headers: { Authorization: `Bearer ${this.token}` },
      });
      const data = await response.json();

      const newNotifications = data.results || [];

      // Merge with existing (WebSocket might have added some)
      newNotifications.forEach((notif) => {
        if (!this.notifications.find((n) => n.id === notif.id)) {
          this.notifications.unshift(notif);
          this.emitEvent("notification:new", notif);
        }
      });

      console.log(
        `✓ Refreshed. Now have ${this.notifications.length} notifications`,
      );
    } catch (error) {
      console.error("❌ Refresh failed:", error);
    }
  }

  // Helpers
  showToast(notification) {
    // Your toast implementation
    console.log(`🎉 Toast: ${notification.title}`);
  }

  emitEvent(eventName, data) {
    window.dispatchEvent(new CustomEvent(eventName, { detail: data }));
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
    }
  }
}
```

### Usage in React

```javascript
function useNotificationManager(token) {
  const [notifications, setNotifications] = useState([]);
  const [connected, setConnected] = useState(false);
  const managerRef = useRef(null);

  useEffect(() => {
    if (!token) return;

    const manager = new NotificationManager(token);
    managerRef.current = manager;

    // Listen for events
    const handleNew = (e) => {
      setNotifications((prev) => [e.detail, ...prev]);
    };

    const handleRead = (e) => {
      setNotifications((prev) =>
        prev.map((n) => (n.id === e.detail ? { ...n, is_read: true } : n)),
      );
    };

    window.addEventListener("notification:new", handleNew);
    window.addEventListener("notification:read", handleRead);

    // Initialize
    manager.initialize();

    return () => {
      manager.disconnect();
      window.removeEventListener("notification:new", handleNew);
      window.removeEventListener("notification:read", handleRead);
    };
  }, [token]);

  return {
    notifications,
    markAsRead: (id) => managerRef.current?.markAsRead(id),
  };
}

// In your component:
function NotificationCenter() {
  const { notifications, markAsRead } = useNotificationManager(token);

  return (
    <div>
      <h2>Notifications ({notifications.length})</h2>
      {notifications.map((n) => (
        <div key={n.id} className={n.is_read ? "read" : "unread"}>
          <h3>{n.title}</h3>
          <p>{n.message}</p>
          {!n.is_read && (
            <button onClick={() => markAsRead(n.id)}>Mark Read</button>
          )}
        </div>
      ))}
    </div>
  );
}
```

---

## 🎯 Decision Tree

```
Start: Need notifications?
│
├─ First load?
│  └─ Use REST (fetch all) → Then connect WebSocket
│
├─ User clicks "Mark as Read"?
│  └─ Use REST (immediate action)
│
├─ New notification arrives?
│  ├─ If WebSocket connected → Receive via WebSocket (instant)
│  ├─ If WebSocket down → Use REST polling (every 5s)
│  └─ If WebSocket reconnects → Stop polling, use WebSocket
│
├─ Load more / Pagination?
│  └─ Use REST (explicit request)
│
└─ Keep UI updated in real-time?
   └─ Use WebSocket (while connected) + REST fallback
```

---

## 📊 Performance Comparison

| Metric                  | REST Only        | WebSocket Only | Hybrid                 |
| ----------------------- | ---------------- | -------------- | ---------------------- |
| Initial load            | ~300ms           | ~300ms         | ~300ms                 |
| New notification        | 5000ms (polling) | ~20ms          | ~20ms (or 5s fallback) |
| Bandwidth (per notif)   | ~2KB             | ~1KB           | ~1KB                   |
| Server load (100 users) | High             | Medium         | Low                    |
| Complexity              | Low              | High           | Medium                 |
| Reliability             | ✅ High          | ⚠️ Medium      | ✅ Very High           |

---

## 🔐 Handling Token Expiration

```javascript
class NotificationManager {
  // ... existing code ...

  async refreshTokenIfNeeded() {
    const token = localStorage.getItem("access_token");
    const expiresIn = this.getTokenExpiry(token);

    if (expiresIn < 60) {
      // 60 seconds left
      console.log("🔐 Refreshing token...");
      const response = await fetch("/api/v1/users/refresh-token/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          refresh: localStorage.getItem("refresh_token"),
        }),
      });

      const { access } = await response.json();
      localStorage.setItem("access_token", access);
      this.token = access;

      // Reconnect WebSocket with new token
      this.ws.close();
      this.connectWebSocket();
    }
  }

  getTokenExpiry(token) {
    // Decode JWT and calculate seconds until expiry
    const payload = JSON.parse(atob(token.split(".")[1]));
    return Math.floor(payload.exp * 1000 - Date.now()) / 1000;
  }
}
```

---

## ✅ Checklist: Implementation Order

- [ ] **Phase 1**: Implement REST fetch for initial load
- [ ] **Phase 2**: Implement WebSocket connection
- [ ] **Phase 3**: Add reconnection logic with backoff
- [ ] **Phase 4**: Implement REST polling fallback
- [ ] **Phase 5**: Add mark-as-read via REST
- [ ] **Phase 6**: Handle token refresh
- [ ] **Phase 7**: Test all paths (connected, offline, reconnect)

---

## 🧪 Testing All Scenarios

```bash
# Test 1: WebSocket connected
# Expected: New notifications arrive instantly

# Test 2: Stop WebSocket (browser DevTools → Network → WebSocket → Close)
# Expected: Switch to REST polling

# Test 3: Reconnect WebSocket
# Expected: Resume WebSocket, stop polling

# Test 4: Go offline completely
# Expected: Show offline indicator, queue updates

# Test 5: Return online
# Expected: Refresh all notifications, resume normal operation
```

---

## 📚 Summary

| Use Case         | Pattern      | Speed   | Reliability        |
| ---------------- | ------------ | ------- | ------------------ |
| Page load        | REST         | Slower  | ✅                 |
| Real-time alert  | WebSocket    | Instant | ✅ (with fallback) |
| Mark as read     | REST         | Slower  | ✅                 |
| Offline fallback | REST polling | Slower  | ✅                 |
| Network recovery | REST refresh | Slower  | ✅                 |

**The hybrid approach gives you the best of both worlds: Real-time performance with REST reliability.**
