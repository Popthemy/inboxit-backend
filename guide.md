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
