# Compilación e Instalación en iOS desde la Consola

Este documento describe el flujo de trabajo automatizado para construir la aplicación híbrida (React/Capacitor) e instalarla directamente en un dispositivo físico iPhone, utilizando exclusivamente herramientas de línea de comandos, sin necesidad de abrir la interfaz gráfica de Xcode.

## 1. Configurar el Entorno de Xcode

Para que los comandos de compilación nativos funcionen (especialmente si encuentras errores donde falta la herramienta `xcodebuild` o problemas de permisos), asegúrate de tener la ruta completa a Xcode configurada.

Si tu terminal presenta problemas para encontrar el compilador completo o usar herramientas como Cocoapods en entornos restringidos, exporta el directorio temporalmente:
```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
```
*(Alternativamente, de forma permanente usando sudo: `sudo xcode-select -s /Applications/Xcode.app/Contents/Developer`)*

## 2. Compilar Web y Sincronizar Capacitor

Desde el directorio `mobile-hybrid/web`, compila el empaquetado de React/Vite y transfiere los archivos (junto a las dependencias nativas) al proyecto iOS:
```bash
cd mobile-hybrid/web
npm run build
npx cap sync ios
```

## 3. Compilar el Binario iOS (xcodebuild)

Navega al directorio de la plataforma iOS y compila la aplicación indicando un directorio de destino explícito para encontrar fácilmente el `.app` resultante:
```bash
cd ios/App
xcodebuild -workspace App.xcworkspace -scheme App -destination generic/platform=iOS -derivedDataPath ./DerivedData build
```

## 4. Obtener el Identificador del iPhone

Asegúrate de que el iPhone esté conectado (por cable o en la misma red local Wi-Fi) y ejecuta el siguiente comando para ver los dispositivos disponibles:
```bash
xcrun devicectl list devices
```

Copia el `Identifier` (UUID largo) asociado a tu dispositivo. Ejemplo: `F8CC6430-566F-513A-9176-CB2CDB414937`.

## 5. Instalar la App en el Dispositivo (devicectl)

Usando la herramienta `devicectl` (disponible a partir de Xcode 15), inyecta el paquete `.app` generado previamente a tu dispositivo:
```bash
xcrun devicectl device install app --device <TU_UUID> ./DerivedData/Build/Products/Debug-iphoneos/App.app
```

> **Nota:** Si el comando `xcrun devicectl list devices` o la instalación arrojan el error *unable to find utility "devicectl"*, confirma que has ejecutado el paso 1 correctamente, ya que esta herramienta es exclusiva del paquete completo de Xcode y no de las simples *Command Line Tools*.
