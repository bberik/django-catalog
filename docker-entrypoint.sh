#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "Database is ready!"

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn remarcable.wsgi:application --bind 127.0.0.1:8000 --workers 3 &

# Start Nginx
echo "Starting Nginx..."
nginx -g 'daemon off;'