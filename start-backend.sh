#!/bin/bash

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Start the backend server
uvicorn backend.main:app --reload --port 8000
