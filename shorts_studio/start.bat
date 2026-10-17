@echo off
rem Shorts Studio: Windows launcher. First run installs everything (~2 min), later runs start instantly.
setlocal
cd /d "%~dp0"
chcp 65001 >nul

set "PY="
where py >nul 2>nul && (py -3 -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>nul && set "PY=py -3")
if not defined PY (
  where python >nul 2>nul && (python -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>nul && set "PY=python")
)
if not defined PY (
  echo Python 3.11+ topilmadi. https://www.python.org/downloads/ dan o'rnating
  echo va o'rnatishda "Add python.exe to PATH" belgisini qo'ying.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Birinchi ishga tushirish: virtual muhit yaratilmoqda...
  %PY% -m venv .venv || goto :fail
)

rem reinstall dependencies only when requirements.txt changed
fc /b requirements.txt ".venv\requirements.stamp" >nul 2>nul
if errorlevel 1 (
  echo Kutubxonalar o'rnatilmoqda, bir necha daqiqa...
  ".venv\Scripts\python.exe" -m pip install --upgrade pip -q --timeout 60 --retries 10 || goto :fail
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt -q --timeout 60 --retries 10 || goto :fail
  copy /y requirements.txt ".venv\requirements.stamp" >nul
)

".venv\Scripts\python.exe" run.py
pause
exit /b 0

:fail
echo.
echo O'rnatishda xato chiqdi. Yuqoridagi xabarni nusxalab yuboring.
pause
exit /b 1
