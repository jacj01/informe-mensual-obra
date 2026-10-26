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

## 5. Instrucción para Futuras Conversaciones
* **No volver a escanear todo el código ni el repositorio desde cero** a menos que el usuario lo solicite expresamente.
* El contexto, arquitectura, herramientas y estándares ya están asimilados en este archivo.
* Proceder directamente a atender la tarea o requerimiento específico del usuario.
