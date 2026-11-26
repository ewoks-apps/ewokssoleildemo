"""ewoksjob configuration: Redis for the Celery broker, the results and the Ewoks events.

Clients and workers use the same file.
When Redis does not run on the host of the client and the worker, change `localhost` to the Redis host.
"""

CELERY = {
    "broker_url": "redis://localhost:6379/0",
    "result_backend": "redis://localhost:6379/1",
    "result_expires": 600,
    "task_remote_tracebacks": True,
    "broker_connection_retry_on_startup": True,
    "enable_utc": False,
}

EWOKS_EXECUTION = {
    "execinfo": {
        "handlers": [
            {
                "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
                "arguments": [{"name": "url", "value": "redis://localhost:6379/2"}],
            }
        ]
    }
}
