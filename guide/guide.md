You actually already **have the right idea on the backend**, but the issue is:

> ❌ your validation is only running in `validate()`, and it’s being bypassed or not consistently triggered due to how `attrs/config` is shaped during update / partial update / field writes.

Let’s fix this properly and make it **impossible for malformed emails to slip through**.

---

# 🔴 Why malformed emails are still getting saved

In Django REST Framework:

### 1. `validate()` is NOT always enough

It runs, but:

* partial updates (`PATCH`)
* direct field assignment edge cases
* `update()` overrides (if you have one later)
  can bypass assumptions about structure.

---

### 2. Your biggest risk here:

```py
config = attrs.get('config', {})
```

If `config` already exists in instance data, DRF may not re-merge it how you expect.

---

### 3. Also subtle issue:

You mutate:

```py
attrs['config'] = config
```

but you don’t normalize deeply enough before validation.

---

# ✅ The correct fix (robust + production-safe)

You should move validation into **field-level validation**, not only object-level.

---

# ✅ FIX 1 — Add a dedicated config validator

```py
def validate_config(self, config):
    channel = self.initial_data.get("channel")

    if channel == "email":
        emails = config.get("recipient_emails")

        if not isinstance(emails, list):
            raise serializers.ValidationError({
                "recipient_emails": "Must be a list of emails"
            })

        if not emails:
            raise serializers.ValidationError({
                "recipient_emails": "At least one email is required"
            })

        validator = EmailValidator()

        for email in emails:
            try:
                validator(email)
            except DjangoValidationError:
                raise serializers.ValidationError({
                    "recipient_emails": f"Invalid email: {email}"
                })

    return config
```

---

# ✅ FIX 2 — Call it from `validate()`

```py
def validate(self, attrs):
    channel = attrs.get("channel") or getattr(self.instance, "channel", None)

    config = attrs.get("config", getattr(self.instance, "config", {}))

    # backward compatibility
    if "recipient_emails" in attrs and not config.get("recipient_emails"):
        config["recipient_emails"] = attrs.pop("recipient_emails")

    config = self.validate_config(config)

    attrs["config"] = config

    if channel == "sms" and not config.get("phone_number"):
        raise serializers.ValidationError({
            "config": {"phone_number": "Required for sms channel"}
        })

    return attrs
```

---

# 🔥 FIX 3 — (IMPORTANT) enforce at DB boundary too

Even better protection:

## Add model-level validation

```py
def clean(self):
    if self.channel == "email":
        emails = self.config.get("recipient_emails", [])

        validator = EmailValidator()

        for email in emails:
            validator(email)
```

Then ensure save calls clean:

```py
def save(self, *args, **kwargs):
    self.full_clean()
    return super().save(*args, **kwargs)
```

---

# 🚨 Why this is critical

Without DB-level or serializer-level enforcement:

* bad emails get stored
* frontend validation is irrelevant
* future API clients bypass rules
* data corruption accumulates silently

---

# 🧠 Best-practice architecture (what you should aim for)

### 1. Frontend

✔ UX validation only

### 2. Serializer (DRF)

✔ authoritative validation (PRIMARY GUARD)

### 3. Model

✔ final safety net (OPTIONAL but recommended)

---

# 💡 Even better improvement (clean design)

Instead of generic `config: dict`, you can enforce:

```py
class EmailConfigSerializer(serializers.Serializer):
    recipient_emails = serializers.ListField(
        child=serializers.EmailField()
    )
```

Then plug it into RouteSerializer.

This eliminates manual loops completely.

---

# 🚀 Summary

### Why your issue happens:

* validation too loosely coupled
* relying only on object-level `validate()`
* config treated as raw dict

### Fix:

✔ move validation into `validate_config()`
✔ normalize config early
✔ optionally enforce at model level
✔ ideally use nested serializers

---

If you want, I can refactor your entire `RouteSerializer` into a **clean polymorphic design (email/sms/slack each with its own serializer)** — that completely removes these bugs long-term.




## New
You’re trying to build a **usage + analytics system (Stripe-like behavior)**, but right now you’re mixing:

* real-time counters
* daily aggregation
* analytics queries
  all inside one mutable model.

That’s why counters break and dashboards become unreliable.

Below is a **top-to-bottom production-grade design**, with reasoning + tradeoffs.

---

# 🧠 1. Core principle (what you should fix first)

### ❌ Current approach (problematic)

You are doing:

* increment counters inside request flow
* reset `requests_today` manually
* rely on `last_request_at`
* mutate aggregates directly

👉 This causes race conditions, inconsistencies, and wrong analytics.

---

### ✅ Correct principle

> Store immutable “events” OR properly partitioned daily aggregates — never both mixed.

You choose one of two architectures:

---

# 🏗️ OPTION A (Recommended): Event-driven system (best accuracy)

## 1. Message table (source of truth)

```python
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    api_key = models.ForeignKey(APIKey, on_delete=models.SET_NULL, null=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True)

    status = models.CharField(max_length=20)  # success / failed
    created_at = models.DateTimeField(auto_now_add=True)
```

### Why this matters

This becomes your **single source of truth**.

---

## 2. Usage is derived (NOT stored per request)

Instead of updating counters every request:

### Total messages

```sql
SELECT COUNT(*) FROM message WHERE user_id = ?
```

### Messages today

```sql
SELECT COUNT(*) 
FROM message 
WHERE user_id = ? 
AND created_at >= today
```

### Success rate

```sql
SELECT 
  SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
FROM message
WHERE user_id = ?
```

---

## 3. Daily analytics (for charts)

```python
class DailyUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    total = models.IntegerField(default=0)
    success = models.IntegerField(default=0)
    failed = models.IntegerField(default=0)
```

---

## 4. Update flow (important)

Instead of incrementing in request path:

### Option 1 (simple)

Update both Message + DailyUsage in same transaction.

### Option 2 (scalable)

Use async worker (Celery/Kafka consumer).

---

## ✔️ Reason this is best

* 100% accurate history
* no race conditions in counters
* easy analytics queries
* audit log exists
* scalable to millions of events

---

## ❌ Tradeoff

* slightly slower writes (extra insert)
* more DB storage
* requires background aggregation for heavy dashboards

---

# ⚡ OPTION B (your current direction): Counter-based system (faster but fragile)

If you insist on real-time counters:

---

## 1. Fix your models

```python
class UserUsage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    total_requests = models.BigIntegerField(default=0)
    requests_today = models.IntegerField(default=0)
    last_reset_date = models.DateField(null=True)
```

---

## 2. Correct increment logic (IMPORTANT FIX)

```python
from django.db import transaction
from django.db.models import F
from django.utils import timezone

@transaction.atomic
def increment_user_usage(apikey_obj):
    now = timezone.now()
    today = now.date()

    usage, _ = UserUsage.objects.select_for_update().get_or_create(
        user=apikey_obj.route.user
    )

    # reset daily counter safely
    if usage.last_reset_date != today:
        usage.requests_today = 0
        usage.last_reset_date = today

    usage.requests_today = F('requests_today') + 1
    usage.total_requests = F('total_requests') + 1

    usage.save(update_fields=[
        "requests_today",
        "total_requests",
        "last_reset_date"
    ])

    # API key tracking
    apikey_obj.usage_count = F('usage_count') + 1
    apikey_obj.last_used_at = now
    apikey_obj.save(update_fields=["usage_count", "last_used_at"])
```

---

## ✔️ Why this works

* atomic transaction prevents race conditions
* no double increments
* proper daily reset
* consistent counters

---

## ❌ Tradeoffs

* still not audit-safe (no event history)
* hard to fix bad data later
* cannot reconstruct past analytics
* breaks under high concurrency without sharding/redis locks

---

# 📊 3. What your dashboard actually needs (missing pieces)

Your UI requires:

---

## 1. Total Messages

→ from Message table OR counter

---

## 2. Messages Today

→ date-filtered query OR `requests_today`

---

## 3. Success vs Failed

❌ missing completely right now
✔ requires `Message.status`

---

## 4. Messages per Day graph

❌ impossible without:

* Message table OR DailyUsage table

---

## 5. Active API keys

You need:

```python
last_used_at + is_active + usage_count
```

---

## 6. Active Routes

You need:

* last_used_at per route
* or message activity per route

---

# 🧩 4. Recommended final architecture (best practice)

If you want something scalable and production-safe:

## ✔️ Use hybrid model:

### 1. Message table (event log)

* truth source
* immutable

### 2. DailyUsage table (fast dashboard)

* pre-aggregated
* updated async or in transaction

### 3. UserUsage table (optional cache)

* total_requests only (not daily logic)

---

# ⚖️ Summary of tradeoffs

| Approach             | Accuracy  | Speed             | Complexity  | Scalability |
| -------------------- | --------- | ----------------- | ----------- | ----------- |
| Counters only        | ❌ weak    | ✅ fast            | low         | poor        |
| Event log only       | ✅ perfect | ❌ slower queries  | medium      | excellent   |
| Hybrid (recommended) | ✅ best    | ✅ fast dashboards | medium-high | excellent   |

---

# 🚨 Final advice (important)

Your current bug (`total_requests not updating`) is a symptom of a bigger issue:

> You’re treating analytics as a side-effect of request handling instead of a data layer problem.

Fix that structure first, and the rest becomes straightforward.

---

If you want, I can:

* redesign your Django models cleanly
* or convert this into a Stripe-style metering system (very scalable)
* or help you add Redis-based real-time counters safely

Just tell me.
