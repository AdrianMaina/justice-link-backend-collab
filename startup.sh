#!/bin/sh

# Set the FLASK_APP environment variable so Flask knows where to find the app
export FLASK_APP=run.py

# Apply database migrations
echo "Applying database migrations..."
flask db upgrade

# Start the application server
echo "Starting Gunicorn..."
gunicorn run:app