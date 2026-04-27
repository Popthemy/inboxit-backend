Setting up a robust logging system in Django Rest Framework (DRF) is essential for monitoring API performance, debugging production errors, and auditing security events. Below is a production-ready configuration and guidelines on when to use each log level.

## 1. The Configuration (`settings.py`)

Django uses Python’s built-in `logging` module. This setup includes a rotating file handler (to prevent disk overflow) and a console handler for local development.

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/drf_backend.log',
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        # Custom logger for your app logic
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

---

## 2. Guidelines for Log Levels

To keep your logs clean and useful, use the appropriate level for the specific situation.

### `logger.debug()`
**Usage:** Detailed information, typically of interest only when diagnosing problems.
* **Example:** Tracking the flow of a complex algorithm or printing the payload of an incoming request during development.
* *“Entering `process_payment` function with data: {data}”*

### `logger.info()`
**Usage:** Confirmation that things are working as expected.
* **Example:** Successful user login, background task completion, or a new record being created in the database.
* *“User ID 452 successfully updated their profile.”*

### `logger.warning()`
**Usage:** An indication that something unexpected happened, or indicative of some problem in the near future (e.g., ‘disk space low’). The software is still working as expected.
* **Example:** A user tried to access a restricted resource, or a deprecated API endpoint was called.
* *“Rate limit approaching for IP 192.168.1.1.”*

### `logger.error()`
**Usage:** Due to a more serious problem, the software has not been able to perform some function.
* **Example:** A third-party API (like a payment gateway) is down, or a form failed validation due to a system mismatch.
* *“Could not connect to SMS Gateway. Notification not sent.”*

### `logger.exception()`
**Usage:** Specifically used inside `except` blocks. It captures the full stack trace.
* **Example:** Database connection failures or unhandled logic errors.
* **Your Code:**
    ```python
    try:
        user = User.objects.create_user(...)
    except Exception as e:
        # This automatically includes the stack trace
        logger.exception(f"Account creation failed: {e}")
    ```

---

## 3. Best Practices for DRF

* **Don't Log Sensitive Data:** Never log passwords, credit card numbers, or full Auth Tokens. Use placeholders or mask them.
* **Context is King:** Always include identifiers (like `user_id` or `order_uuid`) so you can trace the log back to a specific event.
* **Environment Separation:** Set your console logger to `DEBUG` in development, but keep your file or cloud logs at `INFO` or `WARNING` in production to save space and reduce noise.
* **Centralized Logging:** For production apps, consider sending these logs to a service like **Sentry**, **Loggly**, or **ELK Stack** instead of just a local file.

How complex is the logic you're currently debugging in your project?