// Utilidades del aplicativo Informe Financiero
document.addEventListener('DOMContentLoaded', function () {
  // Marcar alertas como live regions for screen readers
  document.querySelectorAll('.alert').forEach(function (a) {
    if (!a.getAttribute('role')) a.setAttribute('role', 'status');
    if (!a.getAttribute('aria-live')) a.setAttribute('aria-live', 'polite');
  });
  // Auto-ocultar alertas después de 8 segundos (tiempo suficiente para lectores de pantalla)
  document.querySelectorAll('.alert').forEach(function (a) {
    setTimeout(function () {
      a.style.transition = 'opacity .4s';
      a.style.opacity = '0';
      setTimeout(function () { a.remove(); }, 400);
    }, 8000);
  });
});
