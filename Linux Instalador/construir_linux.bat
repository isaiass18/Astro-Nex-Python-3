@echo off
setlocal

set AWS_IP=3.16.216.254
set AWS_USER=ubuntu
set PEM_FILE=..\astronext.pem

echo =========================================
echo    Constructor de Astro-Nex para Linux   
echo =========================================
echo 1. Construir .deb para Ubuntu 22.04
echo 2. Construir .deb para Ubuntu 24.04
echo 3. Construir AppImage Universal
echo =========================================
set /p OPCION="Elige una opcion (1-3): "

if not exist "%PEM_FILE%" (
    echo [ERROR] No se encuentra la llave SSH %PEM_FILE%.
    pause
    exit /b 1
)

if "%OPCION%"=="1" (
    set TARGET_FILE=Astro-Nex-v2.0-beta-Ubuntu22.04-amd64.deb
    set BUILD_CMD=sudo docker build --build-arg UBUNTU_VER=22.04 -t astronex-builder -f 'Linux Instalador/Dockerfile.deb' .
) else if "%OPCION%"=="2" (
    set TARGET_FILE=Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb
    set BUILD_CMD=sudo docker build --build-arg UBUNTU_VER=24.04 -t astronex-builder -f 'Linux Instalador/Dockerfile.deb' .
) else if "%OPCION%"=="3" (
    set TARGET_FILE=Astro-Nex-v2.0-beta-Linux-x86_64.AppImage
    set BUILD_CMD=sudo docker build -t astronex-builder -f 'Linux Instalador/Dockerfile.appimage' .
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
ssh -i "%PEM_FILE%" -o IdentitiesOnly=yes %AWS_USER%@%AWS_IP% "cd astronex-build-tmp && %BUILD_CMD% && sudo docker create --name temp-container astronex-builder && sudo docker cp temp-container:/%TARGET_FILE% . && sudo docker rm temp-container"
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la compilacion en AWS.
    pause
    exit /b %errorlevel%
)

echo.
echo [*] Descargando el archivo %TARGET_FILE% al equipo local...
scp -i "%PEM_FILE%" -o IdentitiesOnly=yes %AWS_USER%@%AWS_IP%:/home/%AWS_USER%/astronex-build-tmp/%TARGET_FILE% .\%TARGET_FILE%

echo.
echo [*] Limpiando el servidor AWS...
ssh -i "%PEM_FILE%" -o IdentitiesOnly=yes %AWS_USER%@%AWS_IP% "rm -rf astronex-build-tmp"

echo.
echo ==============================================================
echo [EXITO] Proceso terminado! 
echo El instalador %TARGET_FILE% fue fabricado en la nube y esta listo.
echo ==============================================================
pause
