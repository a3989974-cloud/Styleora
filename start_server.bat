@echo off
title Luxe Store Server
echo Starting Luxe Store Server...
echo.
echo Server will be available at: http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop the server.
echo.
cd /d "C:\Webapps\myprojects\project_1"
py manage.py runserver 8000
pause