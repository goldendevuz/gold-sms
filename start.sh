#!/bin/bash

set -e  # Exit on any error

# Apply database migrations
make mig

# Collect static files
make collect

# Start the Uvicorn ASGI server
echo "Starting Uvicorn ASGI server..."
make run-asgi