@echo off
rem Download the newest agent files from GitHub (agent.ini stays as it is).
cd /d "%~dp0"
set ZIP=%TEMP%\shorts-studio.zip
set OUT=%TEMP%\shorts-studio
powershell -NoProfile -Command "Invoke-WebRequest https://github.com/najotsoati/smart-helper-bot/archive/refs/heads/claude/ai-video-creation-izxplk.zip -OutFile $env:ZIP; Remove-Item $env:OUT -Recurse -Force -ErrorAction SilentlyContinue; Expand-Archive $env:ZIP -DestinationPath $env:OUT -Force; Copy-Item \"$env:OUT\smart-helper-bot-claude-ai-video-creation-izxplk\agent\*\" . -Exclude agent.ini -Force"
if errorlevel 1 (echo Yangilab bo'lmadi & pause & exit /b 1)
echo Agent yangilandi. Endi Shorts Studio yorlig'ini ishga tushiring.
pause
