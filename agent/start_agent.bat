@echo off
cd /d "%~dp0"
rem Use Blender's own Python, so nothing else has to be installed.
set PY=
for /f "delims=" %%i in ('dir /s /b "C:\Program Files\Blender Foundation\python.exe" 2^>nul') do set PY=%%i
if "%PY%"=="" set PY=python
echo Python: %PY%
"%PY%" agent.py
pause
