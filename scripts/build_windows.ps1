$ErrorActionPreference = "Stop"
$env:MSYSTEM="UCRT64"
$env:CHERE_INVOKING="1"
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Split-Path -Parent $scriptPath

Set-Location $projectRoot

Write-Host "Iniciando compilacion de Astro-Nex con MSYS2 UCRT64..." -ForegroundColor Cyan
# Reemplazar la ruta de MSYS2 si el sistema lo requiere. Por defecto C:\msys64
$bashExec = "C:\msys64\usr\bin\bash.exe"

& $bashExec -l -c "/h/Astro-Nex-1.2.3/scripts/build_windows.sh"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Fallo la compilacion en MSYS2."
    exit $LASTEXITCODE
}

Write-Host "Verificando compilador de Inno Setup..." -ForegroundColor Cyan
$isccOptions = @(
    "C:\Users\isaia\AppData\Local\Programs\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
)

$iscc = $null
foreach ($path in $isccOptions) {
    if (Test-Path $path) {
        $iscc = $path
        break
    }
}

if ($iscc) {
    Write-Host "Compilando instalador Setup final con Inno Setup..." -ForegroundColor Cyan
    & $iscc .\installer.iss
    Write-Host "¡Instalador creado con exito en 'Windows Instalador\Astro-Nex-v2.0-beta-Windows-x64.exe'!" -ForegroundColor Green
} else {
    Write-Warning "No se encontro Inno Setup (ISCC.exe). Se ha creado la version portable en 'Windows Instalador\Astro-Nex', pero para compilar el Setup.exe necesitas instalar Inno Setup 6."
}
