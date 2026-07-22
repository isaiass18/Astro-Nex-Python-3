#!/usr/bin/env bash
# Descarga/actualiza Astro-Nex desde GitHub y ejecuta el instalador Linux.

set -euo pipefail

repository_url="https://github.com/isaiass18/Astro-Nex-Python-3.git"
target_dir="$HOME/Aplicaciones/Astro-Nex-Python-3"

usage() {
    cat <<'EOF'
Uso: install_from_github.sh [--directory RUTA] [opciones del instalador]

Descarga o actualiza Astro-Nex-Python-3 desde GitHub y ejecuta
scripts/install_linux.sh. Por defecto usa:
  ~/Aplicaciones/Astro-Nex-Python-3

Ejemplos:
  ./scripts/install_from_github.sh
  ./scripts/install_from_github.sh --test
  ./scripts/install_from_github.sh --directory ~/Astro-Nex --no-launcher
EOF
}

installer_args=()
while (($#)); do
    case "$1" in
        --directory)
            shift
            if (($# == 0)); then
                echo "Falta la ruta después de --directory." >&2
                exit 2
            fi
            target_dir="$1"
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *) installer_args+=("$1") ;;
    esac
    shift
done

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "Este instalador sólo es compatible con Linux." >&2
    exit 1
fi

if ! command -v git >/dev/null; then
    if command -v apt-get >/dev/null; then
        echo "==> Instalando Git..."
        sudo apt-get update
        sudo apt-get install -y git
    else
        echo "Instala Git y vuelve a ejecutar este script." >&2
        exit 1
    fi
fi

if [[ -e "$target_dir" ]]; then
    if [[ ! -d "$target_dir/.git" ]]; then
        echo "La ruta ya existe y no es un repositorio Git: $target_dir" >&2
        echo "Elige otra con --directory o instala desde esa copia con install_linux.sh." >&2
        exit 1
    fi
    echo "==> Actualizando la copia existente..."
    git -C "$target_dir" pull --ff-only
else
    echo "==> Descargando Astro-Nex desde GitHub..."
    mkdir -p "$(dirname "$target_dir")"
    git clone "$repository_url" "$target_dir"
fi

exec "$target_dir/scripts/install_linux.sh" "${installer_args[@]}"
