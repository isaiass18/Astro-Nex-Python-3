# Construir el instalador de Windows

Esta guía genera `Windows Instalador\Astro-Nex-v2.0-Windows-x64.exe` desde el código
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
Remove-Item "Windows Instalador\*.exe" -ErrorAction SilentlyContinue
& 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe' .\installer.iss
```

La ruta puede variar según la instalación de Inno Setup. El resultado debe ser
`Windows Instalador\Astro-Nex-v2.0-Windows-x64.exe`.

## Verificación final

1. Ejecutar el instalador **en una máquina limpia o después de desinstalar** cualquier versión anterior.
2. Confirmar que existe `C:\Program Files\Astro-Nex-2.0\Astro-Nex.exe` (la carpeta debe llamarse `Astro-Nex-2.0`, no `Astro-Nex` ni `Astro-Nex v2`).
3. Confirmar que **no existe** ninguna carpeta residual `C:\Program Files\Astro-Nex` ni `C:\Program Files\Astro-Nex v2`.
4. Abrir Astro-Nex y comprobar que aparece la ventana principal.
5. Probar botón de lápiz (Modificar Carta) y diálogo de Entradas (`Ctrl+E`).
6. Confirmar que `C:\Windows\Fonts\Astro-Nex.ttf` existe.
7. Comprobar que se generó el acceso directo en el escritorio y que al desinstalar la aplicación se remueva correctamente.

No publicar el instalador hasta completar estas comprobaciones.

## Cambios obligatorios en installer.iss (IMPORTANTE)

### 1. Forzar instalación siempre en `Astro-Nex-2.0`

Por defecto Inno Setup detecta una instalación previa (mismo `AppId`) y actualiza
en la **misma carpeta antigua**, ignorando `DefaultDirName`. Para forzar que
**siempre** instale en `C:\Program Files\Astro-Nex-2.0` sin importar versiones
anteriores, agregar esta línea en la sección `[Setup]`:

```ini
[Setup]
; ... resto de opciones ...
UsePreviousAppDir=no
```

### 2. Limpiar carpetas de versiones beta anteriores

Los usuarios que tuvieron betas anteriores pueden tener las carpetas
`Astro-Nex` o `Astro-Nex v2` en Archivos de programa. El instalador debe
borrarlas automáticamente. Asegurarse de que `[InstallDelete]` contenga
**las tres** entradas:

```ini
[InstallDelete]
Type: filesandordirs; Name: "{autopf}\Astro-Nex"
Type: filesandordirs; Name: "{autopf}\Astro-Nex v2"
Type: files; Name: "{autodesktop}\Astro-Nex.lnk"
Type: files; Name: "{autodesktop}\Astro-Nex v2.lnk"
Type: files; Name: "{commondesktop}\Astro-Nex.lnk"
Type: files; Name: "{commondesktop}\Astro-Nex v2.lnk"
Type: files; Name: "{userdesktop}\Astro-Nex.lnk"
Type: files; Name: "{userdesktop}\Astro-Nex v2.lnk"
```

### Notas sobre Inno Setup 6 (Acceso directo)

En la configuración de `installer.iss`, se agregó explícitamente una tarea para que Inno Setup controle de forma nativa la creación y eliminación del acceso directo en el escritorio. Esto soluciona problemas de versiones pasadas donde el icono no aparecía, o bien, el desinstalador lo dejaba olvidado en el escritorio al finalizar:

```ini
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Icons]
Name: "{autoprograms}\Astro-Nex"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
```

## Detección Inteligente de Bases de Datos Antiguas (Inno Setup)

Para mejorar la experiencia de actualización de los usuarios que ya usaban Astro-Nex (incluyendo versiones anteriores en Python 2), se ha inyectado un script en Pascal en el archivo `installer.iss` (sección `[Code]`).

Dado que todas las versiones de Astro-Nex guardan los datos del usuario en la misma ruta estándar nativa (`C:\Users\<Usuario>\.astronex`), el instalador ahora realiza lo siguiente:
1. Al iniciar (`InitializeWizard`), escanea la ruta del perfil del usuario (`ExpandConstant('{%USERPROFILE}\.astronex')`).
2. Utiliza las funciones `FindFirst` y `FindNext` para buscar archivos de bases de datos (`*.db`).
3. Si detecta bases de datos como `charts.db` o `customloc.db`, inyecta dinámicamente una nueva pantalla informativa (`CreateOutputMsgMemoPage`) justo después de la pantalla de bienvenida.
4. Esta pantalla lista los archivos detectados y le comunica al usuario que sus datos personales e históricos están a salvo y serán reutilizados automáticamente por la nueva versión instalada. No es necesaria ninguna migración manual de archivos.
