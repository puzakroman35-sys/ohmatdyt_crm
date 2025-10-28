#!/bin/bash

# Healthcheck script for the services

# Check if the API is up
if curl -s -f http://api:8000/health; then
  echo "API is healthy"
else
  echo "API is not healthy"
  exit 1
fi

# Check if the frontend is up
if curl -s -f http://frontend:3000/health; then
  echo "Frontend is healthy"
else
  echo "Frontend is not healthy"
  exit 1
fi

# Check if Redis is up
if redis-cli ping; then
  echo "Redis is healthy"
else
  echo "Redis is not healthy"
  exit 1
fi

# Check if the database is up
if pg_isready -h db -p 5432; then
  echo "Database is healthy"
else
  echo "Database is not healthy"
  exit 1
fi

echo "All services are healthy"