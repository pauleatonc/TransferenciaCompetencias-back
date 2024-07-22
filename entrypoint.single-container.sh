#!/bin/bash

# Make sure the script stops on the first error
set -e

# Start Nginx in the background
echo "Starting Nginx..."
service nginx start

# Run Django migrations
echo "Applying Django migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Start Gunicorn with Django
echo "Starting Gunicorn..."
gunicorn transferenciacompetencias.wsgi:application --bind 0.0.0.0:8000

# Optional: Catch and log any errors during startup
trap 'catch' ERR
catch() {
    echo "Error occurred, stopping..."
    # You can add any cleanup or error notification commands here
}

