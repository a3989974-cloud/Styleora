@echo off
cd /d C:\Webapps\myprojects\project_1
title STYLEORA - Starting...
echo ============================================
echo          STYLEORA - Starting Up
echo ============================================
echo.

:: Kill any lingering processes
echo [1/4] Cleaning up old processes...
taskkill /f /im python3.13.exe 2>nul
taskkill /f /im ssh.exe 2>nul
timeout /t 2 /nobreak >nul

:: Start Django server (background)
echo [2/4] Starting Django server...
set PYTHONPATH=C:\Webapps\myprojects\project_1\Lib\site-packages
start /B "" "C:\Users\Toshiba\AppData\Local\Microsoft\WindowsApps\python3.13.exe" manage.py runserver --noreload --skip-checks 0.0.0.0:8000
echo        Local: http://127.0.0.1:8000
timeout /t 3 /nobreak >nul

:: Start SSH tunnel (background)
echo [3/4] Starting public tunnel (styleora.serveo.net)...
start /B "" "C:\Program Files\Git\usr\bin\ssh.exe" -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -i C:\Users\Toshiba\.ssh\serveo_key -N -R styleora:80:127.0.0.1:8000 serveo.net

:: Open browser
echo [4/4] Opening browser...
start http://127.0.0.1:8000/
start https://styleora.serveo.net

echo.
echo ============================================
echo  STYLEORA is running!
echo  Local:  http://127.0.0.1:8000
echo  Public: https://styleora.serveo.net
echo  Admin:  http://127.0.0.1:8000/admin/
echo ============================================
echo.
echo  Press any key to STOP all services...
pause >nul

:: Shutdown
echo Shutting down...
taskkill /f /im python3.13.exe 2>nul
taskkill /f /im ssh.exe 2>nul
echo Done.
