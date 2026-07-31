@echo off
echo ========================================================
echo Iniciando Entorno de Pruebas Linux (NoVNC) LOCALMENTE
echo ========================================================
echo.

echo 1. Encendiendo el Escritorio Virtual en tu Docker de Windows...
docker rm -f linux-desktop 2>nul
docker run -d --name linux-desktop -p 8080:80 -v "%cd%:/root/Desktop/Compartido" dorowu/ubuntu-desktop-lxde-vnc

echo.
echo ========================================================
echo       ESCRITORIO VIRTUAL LINUX LISTO PARA USAR
echo ========================================================
echo.
echo Abre tu navegador web (Chrome, Edge, Firefox) y entra a:
echo http://localhost:8080
echo.
echo Pasos para probar Astro-Nex en el escritorio web:
echo 1. En el escritorio de Linux, abre la carpeta "Compartido"
echo 2. Abre el "LXTerminal" (icono negro abajo) o dale clic derecho a la carpeta y "Open in Terminal".
echo 3. Ejecuta este comando para instalarlo:
echo    sudo apt update ^&^& sudo apt install ./astronex_2.0_amd64.deb
echo 4. Ve al menu de Inicio de Linux -^> Run -^> escribe Astro-Nex.
echo.
echo Para apagar el entorno cuando termines, puedes usar Docker Desktop o correr:
echo docker rm -f linux-desktop
echo ========================================================
pause
