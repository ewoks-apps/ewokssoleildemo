"""ewoksjob configuration: SQLite for the Celery broker, the results and the Ewoks events.

No server is needed. Clients and workers must see the same SQLite files:
run them on the same host.
The SQLite files are in the directory `ewokssoleildemo_sqlite` of the temporary directory of the host.
"""

import os
import tempfile

_SQLITE_DIR = os.path.join(tempfile.gettempdir(), "ewokssoleildemo_sqlite")
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
