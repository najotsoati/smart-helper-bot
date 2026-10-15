@echo off
rem One-time setup: an SSH key so the agent opens its tunnel without a password.
rem Usage: setup_ssh_key.bat root@SERVER_IP
setlocal
set "HOST=%~1"
if "%HOST%"=="" (
  echo Ishlatish: setup_ssh_key.bat root@SERVER_IP
  exit /b 1
)
if not exist "%USERPROFILE%\.ssh\studio_key" ssh-keygen -t ed25519 -N "" -C shorts-studio -f "%USERPROFILE%\.ssh\studio_key"
echo.
echo Server parolini bir marta kiriting:
type "%USERPROFILE%\.ssh\studio_key.pub" | ssh -o StrictHostKeyChecking=accept-new %HOST% "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
echo.
echo Tekshiruv - parol so'ramasligi kerak:
ssh -i "%USERPROFILE%\.ssh\studio_key" -o BatchMode=yes %HOST% "echo OK: kalit ishlayapti"
