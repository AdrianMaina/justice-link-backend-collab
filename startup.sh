#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
flask db upgrade

# Start the application server
echo "Starting Gunicorn..."
gunicorn run:app