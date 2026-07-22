#!/usr/bin/env bash
# Instala Astro-Nex Python 3/GTK3 en Ubuntu y Debian desde este repositorio.

set -euo pipefail

usage() {
    cat <<'EOF'
Uso: ./scripts/install_linux.sh [opciones]

Opciones:
  --no-system-deps  No instala paquetes con apt (para sistemas ya preparados).
  --no-font         No instala Astro-Nex.ttf en el perfil del usuario.
  --no-launcher     No crea el lanzador en el menú de aplicaciones.
  --test            Ejecuta las pruebas automáticas al finalizar.
  -h, --help        Muestra esta ayuda.
EOF
}

install_system_deps=true
install_font=true
create_launcher=true
run_tests=false

while (($#)); do
    case "$1" in
        --no-system-deps) install_system_deps=false ;;
        --no-font) install_font=false ;;
        --no-launcher) create_launcher=false ;;
        --test) run_tests=true ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Opción no reconocida: $1" >&2; usage >&2; exit 2 ;;
    esac
    shift
done

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "Este instalador sólo es compatible con Linux." >&2
    exit 1
fi

if ! command -v python3 >/dev/null; then
    echo "No se encontró python3. Instálalo desde el gestor de paquetes." >&2
    exit 1
fi

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
venv_dir="$project_dir/.venv"

if "$install_system_deps"; then
    if ! command -v apt-get >/dev/null; then
        echo "Sólo se automatiza Ubuntu/Debian. Instala GTK3, PyGObject, Pycairo," >&2
        echo "un compilador C, pkg-config y las cabeceras Python/GTK; después usa" >&2
        echo "la opción --no-system-deps." >&2
        exit 1
    fi

    echo "==> Instalando requisitos de Ubuntu/Debian..."
    sudo apt-get update
    sudo apt-get install -y \
        build-essential python3-venv python3-dev pkg-config \
        libgtk-3-dev gir1.2-gtk-3.0 python3-gi python3-gi-cairo python3-cairo
fi

echo "==> Creando entorno Python..."
python3 -m venv --system-site-packages "$venv_dir"
"$venv_dir/bin/python" -m pip install --upgrade pip setuptools wheel
"$venv_dir/bin/python" -m pip install pytz configobj Pillow ipython

echo "==> Compilando el motor astronómico..."
(cd "$project_dir" && "$venv_dir/bin/python" setup.py build_ext --inplace)

if "$install_font"; then
    echo "==> Instalando tipografía astrológica para este usuario..."
    fonts_dir="${XDG_DATA_HOME:-$HOME/.local/share}/fonts"
    mkdir -p "$fonts_dir"
    install -m 644 "$project_dir/astronex/resources/Astro-Nex.ttf" "$fonts_dir/Astro-Nex.ttf"
    command -v fc-cache >/dev/null && fc-cache -f "$fonts_dir" || true
fi

if "$create_launcher"; then
    echo "==> Creando lanzador de aplicaciones..."
    apps_dir="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
    mkdir -p "$apps_dir"
    cat > "$apps_dir/astronex.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Astro-Nex
Comment=Astrological charts
Exec=$venv_dir/bin/python $project_dir/nex.py
Icon=$project_dir/astronex/resources/iconex-48.png
Terminal=false
Categories=Education;Science;
EOF
fi

if "$run_tests"; then
    echo "==> Ejecutando pruebas..."
    (cd "$project_dir" && "$venv_dir/bin/python" -m unittest discover -s tests -q)
fi

cat <<EOF

Instalación completada.

Para iniciar Astro-Nex desde una Terminal:
  $venv_dir/bin/python $project_dir/nex.py
EOF

if "$create_launcher"; then
    echo 'También debería aparecer como "Astro-Nex" en el menú de aplicaciones.'
fi
