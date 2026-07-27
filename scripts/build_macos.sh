#!/usr/bin/env bash
# Build the self-contained macOS Apple Silicon package for Astro-Nex.
set -euo pipefail

project_dir=$(cd "$(dirname "$0")/.." && pwd)
output_dir="$project_dir/Mac Instalador"
version=2.0-beta
architecture=arm64
# Every build has a distinct filename, so a browser or Finder cannot silently
# reopen an older DMG with the same name. BUILD_ID permits a release label;
# otherwise the local build timestamp is used.
build_id=${BUILD_ID:-$(date +%Y%m%d-%H%M%S)}
dmg_path="$output_dir/Astro-Nex-$version-$build_id-macos-$architecture.dmg"

if [[ $(uname -s) != Darwin || $(uname -m) != arm64 ]]; then
    echo "This script builds the Apple Silicon (arm64) macOS installer."
    exit 1
fi

command -v brew >/dev/null || { echo "Homebrew is required."; exit 1; }
command -v hdiutil >/dev/null || { echo "macOS hdiutil is required."; exit 1; }

if pgrep -f '/Astro-Nex.app/Contents/MacOS/Astro-Nex' >/dev/null; then
    echo "Close Astro-Nex before building a new DMG."
    exit 1
fi

if hdiutil info | grep -Fq "$output_dir/Astro-Nex-"; then
    echo "Eject the mounted Astro-Nex DMG before building a new one."
    exit 1
fi

harfbuzz_prefix=$(brew --prefix harfbuzz)
python_bin=${PYTHON_BIN:-python3}
venv_dir="$project_dir/.venv-macos-build"
build_dir=$(mktemp -d /tmp/astronex-macos.XXXXXX)

mkdir -p "$output_dir"
"$python_bin" -m venv --system-site-packages "$venv_dir"
python="$venv_dir/bin/python"

"$python" -m pip install --upgrade \
    pip setuptools wheel pyinstaller pytz configobj Pillow ipython
"$python" -m pip install -e "$project_dir"

"$python" -m PyInstaller --noconfirm --clean --windowed \
    --name Astro-Nex \
    --osx-bundle-identifier org.astronex.app \
    --paths "$project_dir" \
    --hidden-import pysw \
    --hidden-import _pysw \
    --hidden-import PIL.Image \
    --hidden-import PIL.ImageOps \
    --collect-all gi \
    --collect-all cairo \
    --add-data "$project_dir/astronex/resources:astronex/resources" \
    --add-data "$project_dir/astronex/db:astronex/db" \
    --add-data "$project_dir/astronex/locale:astronex/locale" \
    --distpath "$build_dir/dist" \
    --workpath "$build_dir/build" \
    --specpath "$build_dir" \
    "$project_dir/macos_entry.py"

app_path="$build_dir/dist/Astro-Nex.app"
harfbuzz_bundle="$app_path/Contents/Frameworks/PIL/.dylibs/libharfbuzz.0.dylib"

# Pillow bundles a HarfBuzz library incompatible with GTK from Homebrew.
# Replace it with Homebrew's library and bind its dependencies to the app's
# Frameworks directory, so the resulting app does not depend on Homebrew.
cp "$harfbuzz_prefix/lib/libharfbuzz.0.dylib" "$harfbuzz_bundle"
install_name_tool -id @rpath/libharfbuzz.0.dylib "$harfbuzz_bundle"
install_name_tool -change "$harfbuzz_prefix/lib/libfreetype.6.dylib" \
    @rpath/libfreetype.6.dylib "$harfbuzz_bundle"
install_name_tool -change "$(brew --prefix glib)/lib/libglib-2.0.0.dylib" \
    @rpath/libglib-2.0.0.dylib "$harfbuzz_bundle"
install_name_tool -change "$(brew --prefix graphite2)/lib/libgraphite2.3.dylib" \
    @rpath/libgraphite2.3.dylib "$harfbuzz_bundle"
codesign --force --deep --sign - "$app_path"
codesign --verify --deep --strict "$app_path"

hdiutil create -ov -volname "Astro-Nex $version" -srcfolder "$app_path" \
    -format UDZO "$dmg_path"

echo "Created: $dmg_path"
shasum -a 256 "$dmg_path"
