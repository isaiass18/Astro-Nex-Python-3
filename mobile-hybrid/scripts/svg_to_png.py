#!/usr/bin/env python3
"""
Convierte app_chart.svg a app_chart.png usando CairoSVG o rsvg-convert.
En macOS usa el comando 'qlmanage' para renderizar el SVG a PNG.
"""
import subprocess, sys, os

svg_path = os.path.join(os.path.dirname(__file__), '../comparisons/app_chart.svg')
png_path = os.path.join(os.path.dirname(__file__), '../comparisons/app_chart.png')

svg_abs = os.path.abspath(svg_path)
png_abs = os.path.abspath(png_path)

# Intenta con qlmanage de macOS
print(f"Convirtiendo {svg_abs} -> {png_abs}")
result = subprocess.run(
    ['qlmanage', '-t', '-s', '1000', '-o', os.path.dirname(png_abs), svg_abs],
    capture_output=True, text=True
)
print(result.stdout)
print(result.stderr)

# qlmanage genera con sufijo .png pero el nombre incluye extensión original
import glob, shutil
candidates = glob.glob(os.path.dirname(png_abs) + '/app_chart.svg*.png')
if candidates:
    shutil.move(candidates[0], png_abs)
    print(f"PNG guardado en: {png_abs}")
else:
    print("No se encontró PNG generado. Candidatos:")
    for f in glob.glob(os.path.dirname(png_abs) + '/*'):
        print(' ', f)
    sys.exit(1)
