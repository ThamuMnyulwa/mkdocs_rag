#!/bin/bash

set -e

cleanup() {
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

if [ ! -f backend/.env ]; then
    echo "Error: backend/.env not found. Run ./setup.sh first"
    exit 1
fi

if [ ! -d backend/chroma_db ]; then
    echo "Indexing documentation..."
    cd backend
    uv run python -m scripts.index_docs
    cd ..
fi

echo "Starting backend..."
cd backend
uv run uvicorn main:app --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "Starting frontend..."
cd frontend
mkdocs serve > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 2

echo ""
echo "Services running:"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:8000 (or 8001)"
echo ""
echo "Press Ctrl+C to stop"
echo ""

wait
