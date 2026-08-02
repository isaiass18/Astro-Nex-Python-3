#!/bin/bash
set -e

AWS_IP="3.16.216.254"
AWS_USER="ubuntu"
PEM_FILE="../astronext.pem"

echo "========================================="
echo "   Constructor de Astro-Nex para Linux   "
echo "========================================="
echo "1. Construir AppImage autocontenido y .deb integrador"
echo "2. Construir AppImage Universal"
echo "========================================="
read -p "Elige una opción (1-2): " OPCION

if [ ! -f "$PEM_FILE" ]; then
    echo "[ERROR] No se encuentra la llave SSH $PEM_FILE."
    exit 1
fi

chmod 400 "$PEM_FILE"

if [ "$OPCION" = "1" ]; then
    TARGET_FILE="Astro-Nex-v2.0-beta-Ubuntu24.04-amd64.deb"
    APPIMAGE_FILE="Astro-Nex-v2.0-beta-Linux-x86_64.AppImage"
    BUILD_CMD="sudo docker build -t astronex-builder -f 'Linux Instalador/Dockerfile.appimage' . && sudo docker build -t astronex-deb-builder -f 'Linux Instalador/Dockerfile.deb' ."
    EXTRACT_CMD="sudo docker create --name temp-container-deb astronex-deb-builder && sudo docker cp temp-container-deb:/$TARGET_FILE . && sudo docker rm temp-container-deb && sudo docker create --name temp-container-appimage astronex-builder && sudo docker cp temp-container-appimage:/$APPIMAGE_FILE . && sudo docker rm temp-container-appimage"
elif [ "$OPCION" = "2" ]; then
    TARGET_FILE="Astro-Nex-v2.0-beta-Linux-x86_64.AppImage"
    BUILD_CMD="sudo docker build -t astronex-builder -f 'Linux Instalador/Dockerfile.appimage' ."
    EXTRACT_CMD="sudo docker create --name temp-container astronex-builder && sudo docker cp temp-container:/$TARGET_FILE . && sudo docker rm temp-container"
else
    echo "Opción no válida."
    exit 1
fi

echo ""
echo "[*] Conectando a AWS y preparando entorno Docker..."
ssh -i "$PEM_FILE" -o IdentitiesOnly=yes -o ServerAliveInterval=60 -o StrictHostKeyChecking=no "$AWS_USER@$AWS_IP" "sudo apt-get update && sudo apt-get install -y docker.io"

echo ""
echo "[*] Descargando código fresco y compilando (esto tomará varios minutos)..."
ssh -i "$PEM_FILE" -o IdentitiesOnly=yes -o ServerAliveInterval=60 "$AWS_USER@$AWS_IP" "sudo docker system prune -f && rm -rf astronex-build-tmp && mkdir astronex-build-tmp && cd astronex-build-tmp && git clone https://github.com/isaiass18/Astro-Nex-Python-3.git ."
scp -i "$PEM_FILE" -r -o IdentitiesOnly=yes -o StrictHostKeyChecking=no "../Linux Instalador" "$AWS_USER@$AWS_IP:~/astronex-build-tmp/"
ssh -i "$PEM_FILE" -o IdentitiesOnly=yes -o ServerAliveInterval=60 "$AWS_USER@$AWS_IP" "cd astronex-build-tmp && $BUILD_CMD && $EXTRACT_CMD"

echo ""
echo "[*] Descargando los instaladores al equipo local..."
if [ "$OPCION" = "1" ]; then
    scp -i "$PEM_FILE" -o IdentitiesOnly=yes -o ServerAliveInterval=60 "$AWS_USER@$AWS_IP:/home/$AWS_USER/astronex-build-tmp/$TARGET_FILE" "./$TARGET_FILE"
    scp -i "$PEM_FILE" -o IdentitiesOnly=yes -o ServerAliveInterval=60 "$AWS_USER@$AWS_IP:/home/$AWS_USER/astronex-build-tmp/$APPIMAGE_FILE" "./$APPIMAGE_FILE"
else
    scp -i "$PEM_FILE" -o IdentitiesOnly=yes -o ServerAliveInterval=60 "$AWS_USER@$AWS_IP:/home/$AWS_USER/astronex-build-tmp/$TARGET_FILE" "./$TARGET_FILE"
fi

echo ""
echo "[*] Limpiando el servidor AWS..."
ssh -i "$PEM_FILE" -o IdentitiesOnly=yes -o ServerAliveInterval=60 "$AWS_USER@$AWS_IP" "rm -rf astronex-build-tmp"

echo ""
echo "=============================================================="
echo "[ÉXITO] ¡Proceso terminado!"
echo "El instalador $TARGET_FILE fue fabricado en la nube y está listo."
echo "=============================================================="
