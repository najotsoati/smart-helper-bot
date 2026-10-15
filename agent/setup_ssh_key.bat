@echo off
rem One-time setup: an SSH key so the agent can open its tunnel without a password.
setlocal
set /p HOST=Server (masalan root@201.51.10.112): 
if not exist "%USERPROFILE%\.ssh\studio_key" (
  ssh-keygen -t ed25519 -N "" -C shorts-studio -f "%USERPROFILE%\.ssh\studio_key"
)
echo.
echo Server parolini bir marta kiriting:
type "%USERPROFILE%\.ssh\studio_key.pub" | ssh -o StrictHostKeyChecking=accept-new %HOST% "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
findstr /c:"IdentityFile ~/.ssh/studio_key" "%USERPROFILE%\.ssh\config" >nul 2>&1 || (
  for /f "tokens=2 delims=@" %%h in ("%HOST%") do (
    echo.>> "%USERPROFILE%\.ssh\config"
    echo Host %%h>> "%USERPROFILE%\.ssh\config"
    echo   IdentityFile ~/.ssh/studio_key>> "%USERPROFILE%\.ssh\config"
  )
)
echo.
echo Tekshiruv (parol so'ramasligi kerak):
ssh -o BatchMode=yes %HOST% "echo OK: kalit ishlayapti"
pause
