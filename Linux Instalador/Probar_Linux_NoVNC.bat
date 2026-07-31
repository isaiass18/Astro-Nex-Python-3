@echo off
echo ========================================================
echo Iniciando Entorno de Pruebas Linux (NoVNC) en AWS...
echo ========================================================
echo.

echo 1. Subiendo instalador .deb (si no existe) y encendiendo Escritorio...
scp -o StrictHostKeyChecking=no -o IdentitiesOnly=yes -i ..\astronext.pem astronex_2.0_amd64.deb ubuntu@3.16.216.254:/home/ubuntu/ 2>nul

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
echo 4. Ve al menu de Inicio de Linux -^> Run -^> escribe Astro-Nex (o buscalo en aplicaciones).
echo.
echo [ATENCION] Manten esta ventana negra abierta para que funcione el navegador.
echo ========================================================

ssh -o StrictHostKeyChecking=no -o IdentitiesOnly=yes -i ..\astronext.pem -L 8080:localhost:8080 ubuntu@3.16.216.254 "sudo docker rm -f linux-desktop 2>nul ; sudo docker run -d --name linux-desktop -p 8080:80 -v /home/ubuntu:/root/Desktop/Compartido dorowu/ubuntu-desktop-lxde-vnc ; echo Listo, no cierres la ventana ; sleep 3600"
