@echo off
echo ===================================================
echo   GameHub - Automated Setup Script (Windows)
echo ===================================================
echo.

echo [1/3] Installing Root / Backend Dependencies...
call npm install
if %errorlevel% neq 0 (
echo Error installing backend dependencies!
pause
exit /b %errorlevel%
)

echo.
echo [2/3] Installing Frontend Dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
echo Error installing frontend dependencies!
cd ..
pause
exit /b %errorlevel%
)
cd ..

echo.
echo ===================================================
echo   Setup Complete!
echo ===================================================
echo.
echo To start the backend:
echo   node server.js
echo.
echo To start the frontend:
echo   cd frontend ^&^& npm run dev
echo.
pause