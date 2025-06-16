#!/bin/bash

echo "🚀 Starting AI Dev Platform on Railway..."

# Copy the simplified server to backend
cp railway-server.js backend/

# Start the unified server
cd backend
node railway-server.js