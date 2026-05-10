@echo off
cd /d C:\Webapps\myprojects\project_1
set PYTHONPATH=C:\Webapps\myprojects\project_1\Lib\site-packages
start /B "" "C:\Users\Toshiba\AppData\Local\Microsoft\WindowsApps\python3.13.exe" manage.py runserver --noreload --skip-checks 0.0.0.0:8000

