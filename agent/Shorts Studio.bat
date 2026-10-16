@echo off
cd /d "%~dp0"
rem Double-click: opens the SSH tunnel, starts the render agent and opens the panel.
set PY=
for /f "delims=" %%i in ('dir /s /b "C:\Program Files\Blender Foundation\python.exe" 2^>nul') do set PY=%%i
if "%PY%"=="" set PY=python
title Shorts Studio agent
"%PY%" agent.py --open
pause
