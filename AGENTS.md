# Memoria de Arquitectura y Estado del Proyecto: Informe Mensual de Obra

## 1. Identidad y Propósito del Aplicativo
* **Nombre:** Informe Mensual de Obra (Versión 1.4.2).
* **Propósito:** Gestión técnica y financiera para obras públicas por administración directa en Perú.
* **Normativa:** Clasificadores SIAF (2.6.2.3), régimen de construcción civil (CAPECO / R.M. N° 197-2025-TR), D.L. 728 y Directiva N° 017-2023-CG/GMPL (Anexos 07 al 19 para liquidación técnica-financiera).

## 2. Arquitectura de Software
* **Backend:** Python 3 (`informe_web/app.py` factoría `create_app()`, `informe_web/helpers.py`, `informe_web/models.py`, `informe_web/planilla.py`).
* **Base de datos (Multi-tenant SQLite):**
  * Maestra (`instance/informe.db`): usuarios globales, roles (`Super Usuario`, `Administrador`), suscripción y licencias criptográficas HMAC-SHA256.
  * Tenant (`instance/datos/admin_<id>/informe.db`): proyecto, gastos, almacén, tareo, liquidación y operadores secundarios. Conmutación dinámica vía `bind_session(engine)`.
  * Migraciones: automáticas e idempotentes vía `databases.py` / `_alinear_tabla` mediante `PRAGMA table_info`.
* **Servidor local:** Waitress en puerto 5000 (`servidor_silencioso.py` / `iniciar_local.bat`).
* **Frontend:** Jinja2 (87 plantillas en `informe_web/templates/`), Vanilla CSS (`style.css`, `print.css`), JS vanilla, Bootstrap Icons.

## 3. Servidores MCP y Skills Configurados
* Servidores MCP registrados en `.agents/mcp_config.json` y `.agents/plugins/workspace-tools/`:
  * `playwright`: automatización y pruebas de navegador (usando Microsoft Edge).
  * `excel`: `C:\Users\JOHN\.local\bin\uvx.exe excel-mcp-server stdio` para automatización de libros de cálculo.
  * `image`: `@cjkihl/mcp-image`.
  * `canva`: SSE remoto `https://mcp.canva.com/mcp`.
* Skills activos (19 en total en `.agents/skills/` y registrados en `.agents/skills.json`): `excel-automation`, `excel-mcp`, `frontend-design`, `text-review`, `accessibility`, `animate`, etc.

## 4. Estándares de Diseño e Impresión Establecidos
* **Párrafos en hojas de impresión (`.sec-parrafo`):** Deben usar `white-space: normal; text-align: justify; text-justify: inter-word;` para fluir continuos de margen a margen sin saltos de línea artificiales.
* **Tablas en hojas de impresión (`table.tabla`):** Deben usar `table-layout: fixed; width: 100%; box-sizing: border-box;`, celdas de números con `white-space: nowrap;`, y anchos de columnas en porcentajes (`<colgroup>`) sumando exactamente el 100% para jamás desbordar los márgenes de la hoja A4 (174.4 mm útiles).
* **Botón «Volver» en hojas de impresión:** Debe incluir siempre `onclick="window.close(); if (!window.closed) window.location.href = this.href; return false;"` para cerrar la pestaña generada y regresar a la pestaña de origen.

## 5. Reglas Técnicas y Mejoras Recientes Asimiladas
* **CI/CD Automatizado de Releases:** `.github/workflows/release.yml` se dispara automáticamente en cada `push` a `master` cuando cambia `informe_web/version.py`, el propio workflow o se sube un tag `v*`. Compila el instalador Inno Setup (`.exe`) y el paquete de actualización (`.zip` con checksum SHA-256) directamente en GitHub Releases sin intervención manual.
* **Precisión Numérica en Precios y Almacén:** Soporte de P.U hasta con 6 decimales (`data-decimales="6"`, `round(..., 6)` y filtro Jinja `| pu`). El saldo físico y valorizado en almacén se ajusta a `0.00` cuando la cantidad remanente es $\le 0.0001$ para evitar diferencias o céntimos negativos residuales.
* **Auto-reinicio del Servidor Silencioso:** `iniciar_sin_consola.vbs` y `servidor_silencioso.py --reiniciar` liberan automáticamente el puerto 5000 y levantan una instancia limpia en menos de un segundo tras cambios en el código.
* **Formularios Flexibles:** La validación global en `base.html` respeta los atributos `novalidate` y `data-no-validar`, permitiendo guardar formularios (como el Informe Final de Obra) con campos vacíos o progresivos sin bloqueos en el navegador.
* **Documentación del Informe Final (Anexo N° 02):** La relación de los 20 documentos por adjuntar cuenta con casillas interactivas, auto-guardado en tiempo real por AJAX (`/informe_final/guardar_documentos`) y sincronización automática antes de imprimir, reflejando únicamente los documentos efectivamente adjuntados en la hoja de impresión.

## 6. Instrucción para Futuras Conversaciones
* **No volver a escanear todo el código ni el repositorio desde cero** a menos que el usuario lo solicite expresamente.
* El contexto, arquitectura, herramientas, reglas y estándares ya están asimilados en este archivo.
* Proceder directamente a atender la tarea o requerimiento específico del usuario.
