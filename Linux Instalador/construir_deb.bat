@echo off
setlocal

set AWS_IP=3.138.192.48
set AWS_USER=ubuntu
set PEM_FILE=..\astronext.pem

echo Iniciando proceso de construccion de Astro-Nex para Linux via AWS...
echo.

if not exist "%PEM_FILE%" (
    echo [ERROR] No se encuentra la llave SSH %PEM_FILE%.
    pause
    exit /b 1
)

echo 1. Conectando a AWS y preparando entorno Docker...
ssh -i "%PEM_FILE%" -o IdentitiesOnly=yes -o StrictHostKeyChecking=no %AWS_USER%@%AWS_IP% "sudo apt-get update && sudo apt-get install -y docker.io"
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la conexion a AWS o instalacion de Docker.
    pause
    exit /b %errorlevel%
)

echo.
echo 2. Descargando codigo fresco y compilando en Ubuntu 18.04 (esto tomara varios minutos)...
ssh -i "%PEM_FILE%" -o IdentitiesOnly=yes %AWS_USER%@%AWS_IP% "rm -rf astronex-build-tmp && mkdir astronex-build-tmp && cd astronex-build-tmp && git clone https://github.com/isaiass18/Astro-Nex-Python-3.git . && sudo docker build -t astronex-linux-builder -f 'Linux Instalador/Dockerfile' . && sudo docker create --name temp-deb-container astronex-linux-builder && sudo docker cp temp-deb-container:/astronex_2.0_amd64.deb . && sudo docker rm temp-deb-container"
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la compilacion en AWS.
    pause
    exit /b %errorlevel%
)

echo.
echo 3. Descargando el archivo .deb final a Windows...
scp -i "%PEM_FILE%" -o IdentitiesOnly=yes %AWS_USER%@%AWS_IP%:/home/%AWS_USER%/astronex-build-tmp/astronex_2.0_amd64.deb .\astronex_2.0_amd64.deb

echo.
echo 4. Limpiando el servidor AWS...
ssh -i "%PEM_FILE%" -o IdentitiesOnly=yes %AWS_USER%@%AWS_IP% "rm -rf astronex-build-tmp"

echo.
echo ==============================================================
echo [EXITO] ¡Proceso terminado! 
echo El instalador astronex_2.0_amd64.deb fue fabricado en la nube
echo y esta listo en esta carpeta local de Windows.
echo ==============================================================
pause
