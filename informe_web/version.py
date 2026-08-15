"""Version del aplicativo Informe Mensual de Obra.

Se usa para el chequeo de actualizaciones: GitHub Actions lee este valor al
construir la release, y la app lo expone vía GET /api/version.
"""
__version__  = "1.0.3"
