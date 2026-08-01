#!/bin/bash
set -e

# Asegurar que estamos en la raiz del proyecto
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "=> Creando entorno virtual en /h/AstroNex-build-env..."
python -m venv --system-site-packages /h/AstroNex-build-env
source /h/AstroNex-build-env/bin/activate

echo "=> Instalando dependencias y compilando extension nativa..."
python -m pip install configobj
python -m pip install --force-reinstall --no-deps .

echo "=> Generando ejecutable con PyInstaller..."
python -m PyInstaller --noconfirm --clean --windowed \
  --name Astro-Nex \
  --icon astronex/resources/nex-beta.ico \
  --paths . \
  --hidden-import pysw \
  --hidden-import _pysw \
  --collect-all gi \
  --collect-all cairo \
  --collect-all PIL \
  --add-data=astronex/resources:astronex/resources \
  --add-data=astronex/db:astronex/db \
  --add-data=astronex/locale:astronex/locale \
  --distpath /h/AstroNex-frozen-dist \
  --workpath /h/AstroNex-pyinstaller-build \
  windows_entry.py

echo "=> Copiando distribucion portable a 'Windows Instalador/Astro-Nex'..."
rm -rf 'Windows Instalador/Astro-Nex'
cp -a /h/AstroNex-frozen-dist/Astro-Nex 'Windows Instalador/Astro-Nex'

echo "=> Compilacion base completada exitosamente."
