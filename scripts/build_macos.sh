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
dmg_path="$output_dir/Astro-Nex-v$version-macOS-$architecture.dmg"

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
freetype_prefix=$(brew --prefix freetype)
python_bin=${PYTHON_BIN:-python3}
venv_dir="$project_dir/.venv-macos-build"
build_dir=$(mktemp -d /tmp/astronex-macos.XXXXXX)
# Keep the Finder/Dock icon visually distinct from the stable 1.2 release.
icon_source="$project_dir/astronex/resources/nex-beta.ico"
iconset_dir="$build_dir/Astro-Nex.iconset"
icon_path="$build_dir/Astro-Nex.icns"

mkdir -p "$output_dir"
"$python_bin" -m venv --system-site-packages "$venv_dir"
python="$venv_dir/bin/python"

"$python" -m pip install --upgrade \
    pip setuptools wheel pyinstaller pytz configobj Pillow
"$python" -m pip install -e "$project_dir"

# Finder and the Dock require an ICNS icon. Derive it from the same Astro-Nex
# artwork used by the Windows installer so both platforms carry its logo.
# Pillow handles the ICO source reliably, including the large Retina sizes
# required by iconutil.
ICON_SOURCE="$icon_source" ICONSET_DIR="$iconset_dir" "$python" - <<'PY'
import os
from pathlib import Path

from PIL import Image

source = Image.open(os.environ["ICON_SOURCE"]).convert("RGBA")
iconset = Path(os.environ["ICONSET_DIR"])
iconset.mkdir()
for size in (16, 32, 128, 256, 512):
    for pixels, suffix in ((size, ""), (size * 2, "@2x")):
        image = source.resize((pixels, pixels), Image.Resampling.LANCZOS)
        image.save(iconset / f"icon_{size}x{size}{suffix}.png")
PY
iconutil -c icns "$iconset_dir" -o "$icon_path"

"$python" -m PyInstaller --noconfirm --clean --windowed \
    --name Astro-Nex \
    --icon "$icon_path" \
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
frameworks_dir="$app_path/Contents/Frameworks"
harfbuzz_bundle="$frameworks_dir/PIL/.dylibs/libharfbuzz.0.dylib"

# Python 3.14's pyexpat expects a newer Expat API than the system library on
# supported macOS releases. Bundle Homebrew's matching Expat and point the
# extension to it, so the app does not resolve /usr/lib/libexpat.1.dylib.
pyexpat_modules=("$frameworks_dir"/python*/lib-dynload/pyexpat*.so)
if [[ ${#pyexpat_modules[@]} -eq 0 || ! -f "${pyexpat_modules[0]}" ]]; then
    echo "Expected a bundled pyexpat extension."
    exit 1
fi
pyexpat_module="${pyexpat_modules[0]}"
expat_bundle="$frameworks_dir/libexpat.1.dylib"
cp "$(brew --prefix expat)/lib/libexpat.1.dylib" "$expat_bundle"
install_name_tool -id @rpath/libexpat.1.dylib "$expat_bundle"
install_name_tool -change /usr/lib/libexpat.1.dylib \
    @loader_path/../../libexpat.1.dylib "$pyexpat_module"
if ! otool -L "$pyexpat_module" | grep -Fq '@loader_path/../../libexpat.1.dylib'; then
    echo "The bundled pyexpat extension is not linked to the bundled Expat."
    exit 1
fi

# Pillow bundles a HarfBuzz library incompatible with GTK from Homebrew.
# Replace it with Homebrew's library and bind its dependencies to the app's
# Frameworks directory, so the resulting app does not depend on Homebrew.
cp "$harfbuzz_prefix/lib/libharfbuzz.0.dylib" "$harfbuzz_bundle"
install_name_tool -id @rpath/libharfbuzz.0.dylib "$harfbuzz_bundle"
# Homebrew's HarfBuzz records FreeType through its opt path.  The matching
# library is already bundled by Pillow beside HarfBuzz, so use a loader-relative
# reference instead of requiring Homebrew on the user's Mac.
install_name_tool -change "$freetype_prefix/lib/libfreetype.6.dylib" \
    @loader_path/libfreetype.6.dylib "$harfbuzz_bundle"
install_name_tool -change "$(brew --prefix glib)/lib/libglib-2.0.0.dylib" \
    @rpath/libglib-2.0.0.dylib "$harfbuzz_bundle"
install_name_tool -change "$(brew --prefix graphite2)/lib/libgraphite2.3.dylib" \
    @rpath/libgraphite2.3.dylib "$harfbuzz_bundle"

# A distributable app cannot depend on the Homebrew installation that built it.
if find "$app_path/Contents" -type f \( -perm -111 -o -name '*.dylib' \) \
    -exec otool -L {} \; 2>/dev/null | grep -qE '/opt/homebrew|/usr/local/Cellar'; then
    echo "The app still contains a Homebrew library reference; refusing to package it."
    exit 1
fi

codesign --force --deep --sign - "$app_path"
codesign --verify --deep --strict "$app_path"

hdiutil create -ov -volname "Astro-Nex $version" -srcfolder "$app_path" \
    -format UDZO "$dmg_path"

# A successful build supersedes every prior Astro-Nex DMG.  Keeping only this
# artifact prevents a stale installer from being opened or shared by mistake.
find "$output_dir" -maxdepth 1 -type f \
    -name "Astro-Nex-*-macOS-$architecture.dmg" ! -path "$dmg_path" -delete

echo "Created: $dmg_path"
shasum -a 256 "$dmg_path"
