/* ------------------------------------------------------------
   AUTO-AJUSTE AUTOMÁTICO DE COLUMNAS — Hojas de impresión
   - Prohíbe los saltos de línea en números, cabeceras y celdas centradas.
   - Si el ancho natural de un cuadro excede el ancho disponible de la hoja,
     reduce proporcionalmente el tamaño de la letra hasta que todo el cuadro
     quepa en una sola pieza (evita columnas partidas con datos grandes).
   - Tablas con <colgroup> (p. ej. FE-05, una tabla por sección) se agrupan por
     número de columnas: se miden todas juntas, se toma el mayor ancho por
     columna y se aplica el mismo ancho a todas, quedando perfectamente
     alineadas y sin textos que se derramen sobre la columna vecina.
   Se ejecuta solo, para cada tabla.tabla, al cargar la página.
   ------------------------------------------------------------ */
(function () {
  "use strict";

  /* Piso de tamaño de letra en px (~5,3 pt). Por debajo no se reduce. */
  var PISO_PX = 7;

  /* Celdas que nunca deben partir su contenido en dos líneas.
     th.clasif se excluye a propósito: su cabecera puede ocupar 2 líneas. */
  var SIN_SALTO = "th:not(.clasif), td.num, td.ctr, td.right, td.strong, .fila-sub td, .fila-total td, .fila-rubro td";

  function contentWidth(parent) {
    var cs = window.getComputedStyle(parent);
    var padL = parseFloat(cs.paddingLeft) || 0;
    var padR = parseFloat(cs.paddingRight) || 0;
    return Math.max(1, (parent.clientWidth || parent.getBoundingClientRect().width) - padL - padR);
  }

  function bloquearSaltos(tabla) {
    tabla.querySelectorAll(SIN_SALTO).forEach(function (c) {
      if (!c.querySelector("br")) c.style.whiteSpace = "nowrap";
    });
  }

  /* Mide el ancho natural por columna (una sola línea por celda). */
  function medirColumnas(tabla) {
    var cols = tabla.querySelectorAll("colgroup col");
    for (var k = 0; k < cols.length; k++) cols[k].style.width = "auto";
    tabla.style.tableLayout = "auto";
    tabla.style.width = "max-content";

    var anchos = [];
    var filas = tabla.rows;
    for (var r = 0; r < filas.length; r++) {
      var cels = filas[r].cells;
      var ci = 0;
      for (var j = 0; j < cels.length; j++) {
        if (cels[j].colSpan > 1) { ci += cels[j].colSpan; continue; }
        var w = cels[j].offsetWidth;
        if (w > 0 && (!anchos[ci] || w > anchos[ci])) anchos[ci] = w;
        ci++;
      }
    }
    tabla.style.width = "";
    return { count: cols.length, anchos: anchos };
  }

  function reducirFuente(tablas, factor) {
    tablas.forEach(function (t) {
      t.querySelectorAll("th, td").forEach(function (c) {
        var actual = parseFloat(window.getComputedStyle(c).fontSize);
        if (actual > PISO_PX) c.style.fontSize = Math.max(PISO_PX, actual * factor) + "px";
      });
    });
  }

  /* Aplica el ancho medido a cada columna de cada tabla del grupo. */
  function aplicarAnchos(tablas, anchos) {
    tablas.forEach(function (t) {
      var cols = t.querySelectorAll("colgroup col");
      for (var i = 0; i < cols.length; i++) {
        if (anchos[i]) cols[i].style.width = Math.round(anchos[i]) + "px";
      }
      t.style.width = "";
      t.style.tableLayout = "auto";
    });
  }

  /* Caso con <colgroup>: alinear todas las tablas del mismo cuadro. */
  function ajustarGrupo(tablas) {
    var contenedor = tablas[0].parentElement;
    if (!contenedor) { tablas.forEach(ajustarSimple); return; }
    var maxW = contentWidth(contenedor);
    var n = tablas[0].querySelectorAll("colgroup col").length;
    var pasos = 0;
    var anchos = [];
    var total = 0;

    tablas.forEach(bloquearSaltos);

    while (pasos < 7) {
      anchos = new Array(n);
      for (var c = 0; c < n; c++) anchos[c] = 0;
      total = 0;
      tablas.forEach(function (t) {
        var m = medirColumnas(t);
        for (var c2 = 0; c2 < n; c2++) {
          if ((m.anchos[c2] || 0) > anchos[c2]) anchos[c2] = m.anchos[c2];
        }
      });
      anchos.forEach(function (a) { total += a || 0; });
      if (total <= maxW + 1 || pasos === 6) break;
      reducirFuente(tablas, maxW / total);
      pasos++;
    }
    aplicarAnchos(tablas, anchos);
  }

  /* Caso general (sin <colgroup>): ajustar cada cuadro por separado. */
  function ajustarSimple(tabla) {
    var contenedor = tabla.parentElement;
    if (!contenedor) return;
    var maxW = contentWidth(contenedor);

    bloquearSaltos(tabla);

    tabla.style.width = "auto";
    tabla.style.tableLayout = "auto";
    var ancho = tabla.getBoundingClientRect().width;

    var pasos = 0;
    while (ancho > maxW + 1 && pasos < 6) {
      reducirFuente([tabla], maxW / ancho);
      ancho = tabla.getBoundingClientRect().width;
      pasos++;
    }

    tabla.style.tableLayout = "";
    tabla.style.width = "100%";
  }

  function ejecutar() {
    var conGrupo = [], sinGrupo = [];
    document.querySelectorAll("table.tabla").forEach(function (t) {
      (t.querySelector("colgroup col") ? conGrupo : sinGrupo).push(t);
    });

    var grupos = {};
    conGrupo.forEach(function (t) {
      var k = t.querySelectorAll("colgroup col").length;
      (grupos[k] = grupos[k] || []).push(t);
    });
    Object.keys(grupos).forEach(function (k) { ajustarGrupo(grupos[k]); });
    sinGrupo.forEach(ajustarSimple);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ejecutar);
  } else {
    ejecutar();
  }
  window.addEventListener("load", ejecutar);

  window.__autofitImpresion = { ejecutar: ejecutar, ajustar: ajustarSimple, medirColumnas: medirColumnas };
})();