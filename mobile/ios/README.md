# App iOS

La interfaz SwiftUI solicita datos de nacimiento y recibe PNG generados por el
renderer original de Astro-Nex; no reimplementa en Swift la geometría,
símbolos, casas ni aspectos. Incluye el buscador de país y ciudad, las doce
cartas disponibles, fichas y datos técnicos, perfiles locales y la pantalla
de Momento actual con ubicación independiente.

1. Abra `AstroNexMobile.xcodeproj` en Xcode.
2. Cree `AstroNexMobile/Secrets.xcconfig` a partir de
   `AstroNexMobile/Secrets.xcconfig.example`; contiene la URL de render y la
   clave de prueba y está excluido de Git. Las rutas de localidades y detalles
   se derivan de esa misma URL.
3. Para la prueba HTTP inicial, conserve la excepción ATS temporal incluida en
   el `Info.plist`. El paso final debe ser cambiar la URL configurada a HTTPS
   y retirar esa excepción.
4. No incluya una clave de producción en la app: el siguiente paso será
   autenticación de usuarios y claves temporales emitidas por el servidor.
