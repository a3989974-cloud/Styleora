@echo off
title STYLEORA - Live Server
cd /d C:\Webapps\myprojects\project_1

:: Kill old processes
taskkill /f /im python3.13.exe >nul 2>&1
taskkill /f /im ssh.exe >nul 2>&1
timeout /t 2 /nobreak >nul

:: Start Django
set PYTHONPATH=C:\Webapps\myprojects\project_1\Lib\site-packages
start /B "" "C:\Users\Toshiba\AppData\Local\Microsoft\WindowsApps\python3.13.exe" manage.py runserver --noreload --skip-checks 127.0.0.1:8000
echo [OK] Django starting on port 8000...
timeout /t 5 /nobreak >nul

:: Verify Django is up
curl -s -o nul http://127.0.0.1:8000/ 2>nul
if %errorlevel% neq 0 (
    echo [FAIL] Django did not start. Check port 8000.
    pause
    exit /b
)

:: Try serveo.net first (more reliable)
del tunnel_url.txt 2>nul
del tunnel_output.txt 2>nul
echo [OK] Starting tunnel via serveo.net...
start /B "" ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:localhost:8000 serveo.net > tunnel_output.txt 2>&1
timeout /t 15 /nobreak >nul

:: Parse URL from serveo output
for /f "tokens=4" %%a in ('findstr /r "https://.*serveousercontent\.com" tunnel_output.txt') do set URL=%%a
if defined URL goto :show

:: Fallback to localhost.run
echo [OK] Trying localhost.run as fallback...
taskkill /f /im ssh.exe >nul 2>&1
timeout /t 2 /nobreak >nul
del tunnel_output.txt 2>nul
start /B "" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=NUL -o ServerAliveInterval=30 -R 80:localhost:8000 nokey@localhost.run > tunnel_output.txt 2>&1
timeout /t 15 /nobreak >nul
for /f "tokens=*" %%a in ('findstr /r "https://.*\.lhr\.life" tunnel_output.txt') do set URL=%%a

:show
echo %URL% > tunnel_url.txt
echo.
echo ============================================
echo  STYLEORA IS LIVE!
echo ============================================
echo  Public URL: %URL%
echo  Admin:      %URL%/admin/
echo  Local:      http://127.0.0.1:8000/
echo ============================================
echo.
echo  Share the Public URL with anyone.
echo  Close this window to stop the server.
echo.
pause
