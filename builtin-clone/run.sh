#!/bin/sh
# Launch the Built In-style demo clone. Set PORT to override the default.
cd "$(dirname "$0")" || exit 1
exec python3 app.py
