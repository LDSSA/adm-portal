import os
import sys

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    django_settings = os.environ.get("DJANGO_SETTINGS_MODULE")
    if django_settings is None:
        raise SystemExit(
            "Error: `DJANGO_SETTINGS_MODULE` is not set!\n"
            "Set it by running `export DJANGO_SETTINGS_MODULE=adm_portal.settings.dev`"
        )

    print(f"DJANGO_SETTINGS_MODULE = {django_settings}")
    execute_from_command_line(sys.argv)
