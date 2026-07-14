"""Config loading."""
import os
import pathlib

LOCAL_ENV = pathlib.Path(__file__).resolve().parents[1] / "config" / "local.env"


def load():
    values = {}
    for line in LOCAL_ENV.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            values[k.strip()] = v.split("#")[0].strip()
    values.update({k: v for k, v in os.environ.items()
                   if k.startswith("TALLGRASS_") or k == "WAREHOUSE_DSN"})
    return values
