#!/bin/bash
set -e

# Create config directory if it doesn't exist
mkdir -p config

# Check if environment variables are set and write them to files
if [ ! -z "$GOOGLE_CLIENT_SECRET_CONTENT" ]; then
    echo "Writing client_secret.json from environment variable..."
    echo "$GOOGLE_CLIENT_SECRET_CONTENT" > config/client_secret.json
fi

if [ ! -z "$GOOGLE_TOKEN_CONTENT" ]; then
    echo "Writing google_token.json from environment variable..."
    echo "$GOOGLE_TOKEN_CONTENT" > config/google_token.json
fi

# Execute the command passed to the docker container
exec "$@"
