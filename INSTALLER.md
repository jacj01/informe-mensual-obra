# Configuración del Instalador - Informe Mensual de Obra

Documentación técnica del instalador Windows (Inno Setup + Python Embeddable).

## Arquitectura

```
C:\Users\<usuario>\AppData\Local\Programs\InformeObra\  (o {autopf}\InformeObra)
├── python/                    # Python 3.14 Embeddable (descargado de python.org)
│   ├── python.exe
│   ├── pythonw.exe
│   ├── python314._pth          # _pth debe tener "import site" habilitado
│   ├── Lib/
│   │   └── site-packages/      # Flask, waitress, etc. (instalados vía get-pip.py)
│   └── ...                     # DLLs de Python
├── informe_web/                # App Flask
│   ├── app.py
│   ├── servidor_silencioso.py
│   ├── version.py
│   ├── databases.py / helpers.py / models.py
│   ├── static/ / templates/
│   └── instance/               # BD SQLite (creada al primer arranque)
├── iniciar_sin_consola.vbs     # Lanzador principal (doble clic)
├── iniciar_servidor.bat        # Servidor con consola visible (modo red)
├── iniciar_local.bat           # Servidor local (127.0.0.1)
├── detener_servidor.bat        # Mata el proceso por PID
├── actualizar.ps1              # Auto-actualización desde GitHub Releases
├── Logo.ico / Logo.ico
├── unins000.exe                # Desinstalador de Inno Setup
└── instalar_python.bat         # Generado por Inno Setup, se auto-elimina
```

## Problemas conocidos y soluciones

### 1. Python Embeddable no incluye `ensurepip`
- **Causa**: `python -m ensurepip` falla con `No module named ensurepip`
- **Solución**: Descargar `get-pip.py` de `https://bootstrap.pypa.io/get-pip.py` y ejecutarlo
- **Archivo**: `installer.iss` → función `PrepareToInstall` → script `instalar_python.bat`

### 2. Python Embeddable no incluye CWD en `sys.path`
- **Causa**: El archivo `_pth` (ej. `python314._pth`) define `sys.path` y el `.` se refiere al directorio de `python/`, NO al CWD
- **Solución en `servidor_silencioso.py`**: Agregar `sys.path.insert(0, str(BASE))` antes de los imports
- **Solución en `.bat`**: Usar `set "PYTHONPATH=%~dp0informe_web"` antes de ejecutar waitress

### 3. `_pth` y `import site`
- El archivo `python314._pth` tiene `#import site` comentado por defecto
- Para instalar paquetes con pip, se debe descomentar: `import site`
- Inno Setup lo hace en `PrepareToInstall` con PowerShell replace

## Flujo del instalador (Inno Setup)

1. **`PrepareToInstall`** (Pascal Script):
   - Verifica si `python.exe` ya existe → si sí, sale
   - Descarga `python-3.14.0-amd64.zip` de python.org vía PowerShell
   - Descomprime a `{app}\python\`
   - Habilita `import site` en `_pth`
   - Crea `instalar_python.bat` (se ejecuta después en `[Run]`)

2. **`[Files]`**: Copia todos los archivos de la app al `{app}`

3. **`[Run]`**:
   - Ejecuta `instalar_python.bat` (instala pip + Flask/waitress via `get-pip.py`)
   - Ofrece abrir la app al finalizar

## Versión del instalador

- **`installer.iss`** → `#define MyAppVersion "1.0.7"`
- **`informe_web/version.py`** → `__version__ = "1.0.7"`
- Ambos deben coincidir. `version.py` se usa para cache busting CSS y para el auto-updater.

## Publicar nueva versión

1. Actualizar `MyAppVersion` en `installer.iss`
2. Actualizar `__version__` en `informe_web/version.py`
3. Hacer commit + push a `master`
4. Ejecutar `gh workflow run release.yml --ref master`
5. El workflow crea: zip (update) + exe (instalador) como assets del release

## Lanzadores

### `iniciar_sin_consola.vbs` (principal)
- 3-tier detección de Python: embebido → PATH → legacy (`C:\Python314`)
- Usa `WshShell.Run` con ventana oculta (0)
- Si el servidor ya responde, solo abre el navegador
- Si no, lanza `servidor_silencioso.py` en background

### `servidor_silencioso.py`
- Escrito en Python puro (sin dependencias extras)
- Escribe PID en `servidor.pid`
- `detener_anterior()` mata instancias previas por PID
- Abre el navegador automáticamente cuando el servidor responde
- `waitress` sirve la app Flask en `0.0.0.0:5000`

### `actualizar.ps1`
- Descarga el zip del release más reciente desde GitHub
- Parametro `-VersionLocal` (app.py lo pasa como `app.config["INFORME_VERSION"]`)
- Valida que Python exista antes de intentar actualizar

## GitHub Actions (release.yml)

1. Syntax check (AST parse)
2. Clean archivos sensibles (instance/, *.log, *.pid)
3. Build zip con todos los archivos
4. Instalar Inno Setup (`choco install innosetup`)
5. Compilar `.exe` con `ISCC.exe`
6. Crear release con ambos assets

## Notas importantes

- **`PrivilegesRequired=lowest`** → Instalación sin administrador
- **`{autopf}`** con lowest = `AppData\Local\Programs` (no Program Files)
- La BD SQLite se crea en `informe_web/instance/` al primer arranque
- El super usuario se crea automáticamente en `migrar_suscripcion()` (app.py)
- `_seed_inicial()` está deshabilitado (no crea datos de ejemplo)
- El `.gitignore` excluye `instance/`, `*.log`, `*.pid`, `*.estado`, `uploads/`
