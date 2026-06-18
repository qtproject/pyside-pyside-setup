@echo off
cd /d "%~dp0"
uvicorn main:app --host 127.0.0.1 --port 49425
