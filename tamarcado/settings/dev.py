from tamarcado.settings.base import *

DEBUG = True
ALLOWED_HOSTS = []
LOGGING = {
    **LOGGING,
    "loggers": {
        "": {  # '' representa o logger "raíz" (root). Todos "loggers" herdarão dele.
            "level": "DEBUG",
            "handlers": ["console", "file"],
        }
    },
}
