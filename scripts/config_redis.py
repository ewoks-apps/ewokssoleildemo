"""ewoksjob configuration: Redis for the Celery broker, the results and the Ewoks events.

Clients and workers use the same file. Set EWOKS_REDIS_URL when Redis
does not run on this host, for example redis://testbench-host:6379.
"""

import os

_REDIS_URL = os.environ.get("EWOKS_REDIS_URL", "redis://localhost:6379")

CELERY = {
    "broker_url": f"{_REDIS_URL}/0",
    "result_backend": f"{_REDIS_URL}/1",
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
                "arguments": [{"name": "url", "value": f"{_REDIS_URL}/2"}],
            }
        ]
    }
}
