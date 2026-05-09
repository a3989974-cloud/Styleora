@echo off
cd /d C:\Webapps\myprojects\project_1
del tunnel_url.txt 2>nul
del tunnel_output.txt 2>nul
echo [OK] Trying serveo.net...
start /B "" ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:localhost:8000 serveo.net > tunnel_output.txt 2>&1
timeout /t 15 /nobreak >nul
for /f "tokens=*" %%a in ('findstr /r "https://.*serveousercontent\.com" tunnel_output.txt') do set URL=%%a
if defined URL goto :show
echo [OK] Falling back to localhost.run...
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=NUL -o ServerAliveInterval=30 -R 80:localhost:8000 nokey@localhost.run
:show
echo %URL% > tunnel_url.txt
echo Public URL: %URL%
