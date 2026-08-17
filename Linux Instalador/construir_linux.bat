@echo off
setlocal enabledelayedexpansion

set AWS_IP=18.116.201.31
set AWS_USER=ubuntu
set PEM_FILE=..\astronext.pem

echo =========================================
echo    Constructor de Astro-Nex para Linux   
echo =========================================
echo 1. Construir .deb Universal (basado en AppImage)
echo 2. Construir AppImage Universal
echo =========================================
set /p OPCION="Elige una opcion (1-2): "

if not exist "%PEM_FILE%" (
    echo [ERROR] No se encuentra la llave SSH %PEM_FILE%.
    pause
    exit /b 1
)

if "%OPCION%"=="1" (
    set TARGET_FILE=Astro-Nex-v2.0-Ubuntu24.04-amd64.deb
    set APPIMAGE_FILE=Astro-Nex-v2.0-Linux-x86_64.AppImage
    set BUILD_CMD=sudo docker build -t astronex-builder -f "Linux Instalador/Dockerfile.appimage" . ^&^& sudo docker build -t astronex-deb-builder -f "Linux Instalador/Dockerfile.deb" .
    set EXTRACT_CMD=sudo docker create --name temp-container-deb astronex-deb-builder ^&^& sudo docker cp temp-container-deb:/!TARGET_FILE! . ^&^& sudo docker rm temp-container-deb ^&^& sudo docker create --name temp-container-appimage astronex-builder ^&^& sudo docker cp temp-container-appimage:/!APPIMAGE_FILE! . ^&^& sudo docker rm temp-container-appimage
) else if "%OPCION%"=="2" (
    set TARGET_FILE=Astro-Nex-v2.0-Linux-x86_64.AppImage
    set BUILD_CMD=sudo docker build -t astronex-builder -f "Linux Instalador/Dockerfile.appimage" .
    set EXTRACT_CMD=sudo docker create --name temp-container astronex-builder ^&^& sudo docker cp temp-container:/!TARGET_FILE! . ^&^& sudo docker rm temp-container
) else (
    echo Opcion no valida.
    pause
    exit /b 1
)

echo.
echo [*] Conectando a AWS y preparando entorno Docker...
ssh -i "%PEM_FILE%" -o IdentitiesOnly=yes -o StrictHostKeyChecking=no %AWS_USER%@%AWS_IP% "sudo apt-get update && sudo apt-get install -y docker.io"
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la conexion a AWS o instalacion de Docker.
    pause
    exit /b %errorlevel%
)

echo.
echo [*] Descargando codigo fresco y compilando (esto tomara varios minutos)...
ssh -i "%PEM_FILE%" -o IdentitiesOnly=yes %AWS_USER%@%AWS_IP% "sudo docker system prune -f && rm -rf astronex-build-tmp && mkdir astronex-build-tmp && cd astronex-build-tmp && git clone https://github.com/isaiass18/Astro-Nex-Python-3.git ."
scp -i "%PEM_FILE%" -r -o IdentitiesOnly=yes -o StrictHostKeyChecking=no "..\Linux Instalador" "%AWS_USER%@%AWS_IP%:~/astronex-build-tmp/"
ssh -i "%PEM_FILE%" -o IdentitiesOnly=yes %AWS_USER%@%AWS_IP% "cd astronex-build-tmp && %BUILD_CMD% && %EXTRACT_CMD%"
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la compilacion en AWS.
    pause
    exit /b %errorlevel%
)

echo.
echo [*] Descargando los instaladores al equipo local...
if "%OPCION%"=="1" (
    scp -i "%PEM_FILE%" -o IdentitiesOnly=yes %AWS_USER%@%AWS_IP%:/home/%AWS_USER%/astronex-build-tmp/%TARGET_FILE% .\%TARGET_FILE%
    scp -i "%PEM_FILE%" -o IdentitiesOnly=yes %AWS_USER%@%AWS_IP%:/home/%AWS_USER%/astronex-build-tmp/%APPIMAGE_FILE% .\%APPIMAGE_FILE%
) else (
    scp -i "%PEM_FILE%" -o IdentitiesOnly=yes %AWS_USER%@%AWS_IP%:/home/%AWS_USER%/astronex-build-tmp/%TARGET_FILE% .\%TARGET_FILE%
)

echo.
echo [*] Limpiando el servidor AWS...
ssh -i "%PEM_FILE%" -o IdentitiesOnly=yes %AWS_USER%@%AWS_IP% "rm -rf astronex-build-tmp"

echo.
echo ==============================================================
echo [EXITO] Proceso terminado! 
echo El instalador %TARGET_FILE% fue fabricado en la nube y esta listo.
echo ==============================================================
pause
