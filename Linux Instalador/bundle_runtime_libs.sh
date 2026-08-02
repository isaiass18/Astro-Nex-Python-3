#!/usr/bin/env bash
# Bundle non-glibc shared libraries required by Python extensions and GTK.
set -euo pipefail

appdir=${1:?Uso: bundle_runtime_libs.sh RUTA_APPDIR}
libdir="$appdir/usr/lib"
mkdir -p "$libdir"

is_system_library() {
    case "$1" in
        ld-linux-*|libc.so.6|libdl.so.2|libm.so.6|libpthread.so.0|librt.so.1|libresolv.so.2)
            return 0
            ;;
    esac
    return 1
}

resolve_library() {
    local soname=$1 path
    path=$(ldconfig -p | awk -v name="$soname" '$1 == name { print $NF; exit }') || true
    if [[ -n "$path" && -f "$path" ]]; then
        printf '%s\n' "$path"
        return 0
    fi

    path=$(find /lib /usr/lib -type f -name "$soname" -print -quit 2>/dev/null || true)
    [[ -n "$path" ]] && printf '%s\n' "$path"
}

copy_needed_libraries() {
    local changed=0 binary soname source
    while IFS= read -r -d '' binary; do
        while IFS= read -r soname; do
            is_system_library "$soname" && continue
            [[ -e "$libdir/$soname" ]] && continue
            source=$(resolve_library "$soname")
            if [[ -z "$source" ]]; then
                echo "No se pudo resolver $soname requerido por $binary" >&2
                exit 1
            fi
            cp -aL "$source" "$libdir/$soname"
            changed=1
        done < <(readelf -d "$binary" 2>/dev/null | sed -n 's/.*Shared library: \[\([^]]*\)\].*/\1/p')
    done < <(find "$appdir/usr" -type f \( -name '*.so' -o -name '*.so.*' -o -path "$appdir/usr/bin/*" \) -print0)
    # Shell uses zero as success: repeat the outer loop while a library was added.
    return $((1 - changed))
}

# Resolve recursively: a copied library can itself require another library.
while copy_needed_libraries; do :; done

# The AppImage must prefer its bundled ABI libraries, including libffi.so.7.
while IFS= read -r -d '' binary; do
    patchelf --set-rpath '$ORIGIN:$ORIGIN/..:$ORIGIN/../..:$ORIGIN/../../..:$ORIGIN/../../../..' "$binary" 2>/dev/null || true
done < <(find "$appdir/usr" -type f \( -name '*.so' -o -name '*.so.*' -o -path "$appdir/usr/bin/*" \) -print0)

# Fail during the build rather than delivering an AppImage with a missing ABI.
while IFS= read -r -d '' binary; do
    if ! LD_LIBRARY_PATH="$libdir${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" ldd "$binary" 2>&1 | grep -q 'not found'; then
        continue
    fi
    echo "Dependencias sin resolver en $binary:" >&2
    LD_LIBRARY_PATH="$libdir${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" ldd "$binary" >&2 || true
    exit 1
done < <(find "$appdir/usr" -type f \( -name '*.so' -o -name '*.so.*' -o -path "$appdir/usr/bin/*" \) -print0)

test -e "$libdir/libffi.so.7"
