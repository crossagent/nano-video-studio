@echo off
setlocal
set "BLENDER_PY=C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe"
if exist "%BLENDER_PY%" (
    "%BLENDER_PY%" "%~dp0runner.py" %*
) else (
    python "%~dp0runner.py" %*
)
exit /b %ERRORLEVEL%
