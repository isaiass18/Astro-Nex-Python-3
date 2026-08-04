# Astro-Nex 2.0 beta para Windows

Este directorio es el entorno de compilación para el instalador:

```text
Astro-Nex-v2.0-beta-Windows-x64.exe
```

👉 **[Descargar instalador para Windows desde GitHub Releases](https://github.com/isaiass18/Astro-Nex-Python-3/releases/download/v2.0b0/Astro-Nex-v2.0-beta-Windows-x64.exe)**

## Instalación recomendada

1. Ejecuta `Astro-Nex-v2.0-beta-Windows-x64.exe` (descargado desde GitHub).
2. Sigue los pasos del asistente de instalación.
3. Abre Astro-Nex desde el acceso que el instalador crea en Windows.

El instalador incluye Python, GTK3, PyGObject, Pycairo, la extensión
astronómica `_pysw` y los recursos necesarios. No es necesario instalar esos
componentes por separado.

## Aviso de Seguridad (SmartScreen)

Como esta versión beta aún no cuenta con un certificado digital comercial, al abrir el instalador Windows podría mostrar una pantalla azul diciendo *"Windows protegió su PC"*. 

Para continuar la instalación de forma segura:
1. Haz clic en el texto que dice **"Más información"** (debajo de la advertencia).
2. Aparecerá un nuevo botón en la parte inferior; haz clic en **"Ejecutar de todas formas"**.

Usa únicamente copias descargadas directamente de este repositorio oficial.

## Migración manual de datos (desde otro equipo)

Si tienes datos guardados en otro equipo, copia estos archivos y transfiérelos a tu nuevo PC mediante una memoria USB, carpeta compartida o servicio de la nube:

- **`charts.db`**: las personas y cartas creadas.
- **`customloc.db`**: las ubicaciones personalizadas.
- **`cfg.ini`**: la configuración, colores y preferencias.

Las ubicaciones habituales de origen en el equipo anterior son:

- **Linux:** `~/.astronex/`
- **Windows:** `C:\Users\<Usuario>\.astronex\` (o `.astronex-v2\` si ya usabas la nueva versión).
- **Wine:** `drive_c/users/<Usuario>/.astronex/` dentro del prefijo de Wine.

Para colocarlos en tu PC Windows actual:

1. Abre Astro-Nex una vez y ciérralo. Así se crea la nueva carpeta de datos.
2. Abre el **Explorador de Archivos** (tecla `Win + E`).
3. En la barra de direcciones superior, escribe `%USERPROFILE%\.astronex-v2` y presiona **Enter**.
4. Pega los archivos `charts.db`, `customloc.db` y `cfg.ini` transferidos desde el equipo anterior. Si Windows te pregunta, selecciona reemplazar los archivos en el destino (conservando primero una copia de seguridad si lo consideras necesario).

*(Nota: Si estás actualizando desde la versión clásica de Astro-Nex **en este mismo PC**, el programa copiará tus bases de datos automáticamente en su primer inicio; no necesitas hacer este proceso manual).*
