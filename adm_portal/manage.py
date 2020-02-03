import os
import sys

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    if os.environ.get("DJANGO_SETTINGS_MODULE") is None:
        raise SystemExit(
            "Error: `DJANGO_SETTINGS_MODULE` is not set!\n"
            "Set it by running `export DJANGO_SETTINGS_MODULE=adm_portal.settings.dev`"
        )

    execute_from_command_line(sys.argv)
