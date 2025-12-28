#!/bin/sh
set -e
echo "Entrypoint starts"
python manage.py migrate --noinput
echo "Entrypoint have ended"
exec "$@"
