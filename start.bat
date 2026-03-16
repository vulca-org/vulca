@echo off
echo ========================================
echo   VULCA — Quick Start
echo ========================================
echo.

echo [1/3] Initializing database...
cd wenxin-backend
python init_db.py
if %errorlevel% neq 0 (
    echo   Database init skipped (may already exist)
    echo   Continuing...
)
echo   Database ready

echo.
echo [2/3] Starting backend...
start cmd /k "cd /d %cd% && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001"
echo   Backend starting (port 8001)...

echo.
echo [3/3] Starting frontend...
cd ..\wenxin-moyun
start cmd /k "npm run dev"
echo   Frontend starting (port 5173)...

echo.
echo ========================================
echo   All services started!
echo ========================================
echo.
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:8001
echo   API Docs:  http://localhost:8001/docs
echo.
echo   Demo account:  demo / demo123
echo   Admin account: admin / admin123
echo.
echo Press any key to close...
pause > nul
