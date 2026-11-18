"""ewoksjob configuration: SQLite for the Celery broker, the results and the Ewoks events.

No server is needed. Clients and workers must see the same SQLite files:
use a local disk (not NFS or GPFS) and run them on the same host.
Set EWOKS_SQLITE_DIR to change the directory of the SQLite files.
"""

import os

_SQLITE_DIR = os.environ.get(
    "EWOKS_SQLITE_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sqlite"),
)
os.makedirs(_SQLITE_DIR, exist_ok=True)

CELERY = {
    "broker_url": f"sqla+sqlite:///{_SQLITE_DIR}/celery.db",
    "result_backend": f"db+sqlite:///{_SQLITE_DIR}/celery_results.db",
    "result_expires": 600,
    "task_remote_tracebacks": True,
    "broker_connection_retry_on_startup": True,
    "enable_utc": False,
}

EWOKS_EXECUTION = {
    "execinfo": {
        "handlers": [
            {
                "class": "ewoksjob.events.handlers.Sqlite3EwoksEventHandler",
                "arguments": [
                    {"name": "uri", "value": f"file://{_SQLITE_DIR}/ewoks_events.db"}
                ],
            }
        ]
    }
}
