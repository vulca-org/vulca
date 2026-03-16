#!/bin/bash

echo "========================================"
echo "   VULCA — Quick Start"
echo "========================================"
echo ""

echo "[1/3] Initializing database..."
cd wenxin-backend
python3 init_db.py
if [ $? -ne 0 ]; then
    echo "  Database init skipped (may already exist)"
    echo "  Continuing..."
fi
echo "  Database ready"

echo ""
echo "[2/3] Starting backend..."
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!
echo "  Backend starting... (PID: $BACKEND_PID)"

echo ""
echo "[3/3] Starting frontend..."
cd ../wenxin-moyun
npm run dev &
FRONTEND_PID=$!
echo "  Frontend starting... (PID: $FRONTEND_PID)"

echo ""
echo "========================================"
echo "   All services started!"
echo "========================================"
echo ""
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://localhost:8001"
echo "  API Docs:  http://localhost:8001/docs"
echo ""
echo "  Demo account:  demo / demo123"
echo "  Admin account: admin / admin123"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID" INT
wait
