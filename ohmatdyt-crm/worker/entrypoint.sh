#!/bin/sh
set -e

echo "Waiting for Redis and PostgreSQL..."
sleep 5

exec "$@"