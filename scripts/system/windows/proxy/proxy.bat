@echo off

:: Set proxy variables from environment or use default
if defined CB_HTTP_PROXY (
    set CB_HTTP_PROXY=%CB_HTTP_PROXY%
) else (
    set CB_HTTP_PROXY=http://127.0.0.1:7890
)

if defined CB_HTTPS_PROXY (
    set CB_HTTPS_PROXY=%CB_HTTPS_PROXY%
) else (
    set CB_HTTPS_PROXY=%CB_HTTP_PROXY%
)

if /i "%1"=="on" (
    call :EnableProxy
) else if /i "%1"=="off" (
    call :DisableProxy
) else (
    call :ShowHelp
    exit /b 0
)

exit /b 0

:ShowHelp
echo.
echo Proxy Control Script
echo ==========================================
echo Usage:
echo   %~nx0 on     - Enable proxy
echo   %~nx0 off    - Disable proxy
echo.
echo Current HTTP_PROXY : %CB_HTTP_PROXY%
echo Current HTTPS_PROXY: %CB_HTTPS_PROXY%
echo ==========================================
exit /b 0

:EnableProxy
set HTTP_PROXY=%CB_HTTP_PROXY%
set HTTPS_PROXY=%CB_HTTPS_PROXY%
echo [92m[ON][0m HTTP  Proxy %HTTP_PROXY% enabled in CMD
echo [92m[ON][0m HTTPS Proxy %HTTPS_PROXY% enabled in CMD
exit /b 0

:DisableProxy
if defined HTTP_PROXY (
    echo [91m[OFF][0m HTTP  Proxy %HTTP_PROXY% disabled in CMD
    echo [91m[OFF][0m HTTPS Proxy %HTTPS_PROXY% disabled in CMD
    set HTTP_PROXY=
    set HTTPS_PROXY=
) else (
    echo [91m[OFF][0m Proxy disabled in CMD
)
exit /b 0