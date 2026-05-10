@echo off
cd /d C:\Webapps\myprojects\project_1
echo https://styleora.serveo.net > tunnel_url.txt
echo [OK] Starting serveo tunnel to styleora.serveo.net...
"C:\Program Files\Git\usr\bin\ssh.exe" -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -i C:\Users\Toshiba\.ssh\serveo_key -N -R styleora:80:127.0.0.1:8000 serveo.net
