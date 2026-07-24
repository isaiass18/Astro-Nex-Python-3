# Construir el instalador de Windows

Esta guía genera `Windows Instalador\Astro-Nex-Setup.exe` desde el código
actual del repositorio. El resultado es un **instalador**, no sólo una versión
portable: instala también la fuente `Astro-Nex.ttf` en Windows.

## Requisitos

Usar MSYS2 **UCRT64** de 64 bits. No mezclar Python de CPython oficial con
las DLL de GTK de MSYS2.

En la consola UCRT64 instalar:

```bash
pacman -Syu
pacman -S --needed \
  mingw-w64-ucrt-x86_64-python \
  mingw-w64-ucrt-x86_64-python-pip \
  mingw-w64-ucrt-x86_64-python-setuptools \
  mingw-w64-ucrt-x86_64-python-wheel \
  mingw-w64-ucrt-x86_64-python-gobject \
  mingw-w64-ucrt-x86_64-python-cairo \
  mingw-w64-ucrt-x86_64-python-pillow \
  mingw-w64-ucrt-x86_64-python-pytz \
  mingw-w64-ucrt-x86_64-python-ipython \
  mingw-w64-ucrt-x86_64-gtk3 \
  mingw-w64-ucrt-x86_64-gcc \
  mingw-w64-ucrt-x86_64-pyinstaller
```

Instalar también [Inno Setup 6](https://jrsoftware.org/isdl.php). Su compilador
es `ISCC.exe`.

## Preparar una copia limpia

```bash
git clone https://github.com/isaiass18/Astro-Nex-Python-3.git Astro-Nex-Python-3
cd Astro-Nex-Python-3
```

`astronex/resources/ac.pk` es un pickle de protocolo antiguo y **debe
conservar finales de línea LF**. Si Git en Windows usa `core.autocrlf=true`,
restaurar este archivo sin conversión antes de construir:

```bash
git -c core.autocrlf=false checkout HEAD -- astronex/resources/ac.pk
```

Comprobarlo con Python; debe imprimir `acpaths 2`:

```bash
python -c "import pickle; p='astronex/resources/ac.pk'; print('acpaths', len(pickle.load(open(p, 'rb'), encoding='latin1')))"
```

## Crear el entorno y compilar el motor astronómico

Crear el entorno fuera del repositorio evita mezclar resultados de una
compilación previa con el código fuente:

```bash
python -m venv --system-site-packages /h/AstroNex-build-env
source /h/AstroNex-build-env/bin/activate
python -m pip install configobj
python -m pip install --force-reinstall --no-deps .
```

La última orden compila la extensión nativa `_pysw` desde `ext/`.

## Punto de entrada y PyInstaller

Crear `windows_entry.py` en la raíz:

```python
from astronex.nex import cli

if __name__ == "__main__":
    cli()
```

Generar la distribución en modo ventana:

```bash
python -m PyInstaller --noconfirm --clean --windowed \
  --name Astro-Nex \
  --icon astronex/resources/nex.ico \
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
```

Antes de seguir, ejecutar
`/h/AstroNex-frozen-dist/Astro-Nex/Astro-Nex.exe` y confirmar que aparece la
ventana principal, no sólo la imagen de inicio.

Después sustituir el portable que irá dentro del instalador:

```bash
rm -rf 'Windows Instalador/Astro-Nex'
cp -a /h/AstroNex-frozen-dist/Astro-Nex 'Windows Instalador/Astro-Nex'
```

## Crear el instalador

Usar `installer.iss` en la raíz. Debe copiar recursivamente
`Windows Instalador\Astro-Nex\*` a `{app}` y declarar además:

```ini
Source: "Windows Instalador\Astro-Nex\_internal\astronex\resources\Astro-Nex.ttf"; DestDir: "{autofonts}"; FontInstall: "Astro-Nex"; Flags: onlyifdoesntexist uninsneveruninstall
```

Compilar con Inno Setup desde PowerShell:

```powershell
& 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe' .\installer.iss
```

La ruta puede variar según la instalación de Inno Setup. El resultado debe ser
`Windows Instalador\Astro-Nex-Setup.exe`.

## Verificación final

1. Ejecutar el instalador en una ubicación de prueba o desinstalar la versión
   anterior e instalar la nueva.
2. Confirmar que existe `C:\Program Files\Astro-Nex\Astro-Nex.exe`.
3. Abrir Astro-Nex y comprobar que aparece la ventana principal.
4. Probar clic derecho en la carta y F1.
5. Confirmar que `C:\Windows\Fonts\Astro-Nex.ttf` existe.

No publicar el instalador hasta completar estas comprobaciones.
