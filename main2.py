from fastapi import Request
from dotenv import load_dotenv
import yaml
import os

load_dotenv()

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def to_bool(value):
    return str(value).lower() in ["true", "1", "yes", "on"]


@app.get("/effective-config")
def effective_config(request: Request):
    config = DEFAULTS.copy()

    # YAML layer
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml") as f:
            config.update(yaml.safe_load(f) or {})

    # .env layer
    if os.getenv("APP_LOG_LEVEL"):
        config["log_level"] = os.getenv("APP_LOG_LEVEL")

    if os.getenv("NUM_WORKERS"):
        config["workers"] = int(os.getenv("NUM_WORKERS"))

    # OS env layer
    if os.getenv("APP_WORKERS"):
        config["workers"] = int(os.getenv("APP_WORKERS"))

    # CLI overrides (?set=key=value)
    for item in request.query_params.getlist("set"):
        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        if key in ["port", "workers"]:
            config[key] = int(value)

        elif key == "debug":
            config[key] = to_bool(value)

        else:
            config[key] = value

    # Final type coercion
    config["port"] = int(config["port"])
    config["workers"] = int(config["workers"])
    config["debug"] = bool(config["debug"])
    config["log_level"] = str(config["log_level"])

    # Always mask the secret
    config["api_key"] = "****"

    return config
