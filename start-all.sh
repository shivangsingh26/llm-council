#!/bin/bash

echo "🚀 Starting LLM Council..."
echo ""

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Check if ports are available
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8000 is already in use. Killing existing process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 2
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 3000 is already in use. Frontend may start on a different port."
fi

echo ""
echo "📦 Starting Backend (http://localhost:8000)..."
uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

echo ""
echo "🎨 Starting Frontend (http://localhost:3000)..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers are starting!"
echo ""
echo "📍 Backend:  http://localhost:8000"
echo "📍 Frontend: http://localhost:3000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers..."
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
