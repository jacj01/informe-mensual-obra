// Utilidades del aplicativo Informe Financiero
document.addEventListener('DOMContentLoaded', function () {
  // Marcar alertas como live regions for screen readers
  document.querySelectorAll('.alert').forEach(function (a) {
    if (!a.getAttribute('role')) a.setAttribute('role', a.classList.contains('alert-error') ? 'alert' : 'status');
    if (!a.getAttribute('aria-live')) a.setAttribute('aria-live', a.classList.contains('alert-error') ? 'assertive' : 'polite');
  });
  // Auto-ocultar SOLO alertas informativas/success tras 8 s; las de error
  // permanecen visibles hasta que el usuario las cierre (accesibilidad).
  document.querySelectorAll('.alert').forEach(function (a) {
    if (a.classList.contains('alert-error')) return;
    setTimeout(function () {
      a.style.transition = 'opacity .4s';
      a.style.opacity = '0';
      setTimeout(function () { a.remove(); }, 400);
    }, 8000);
  });
});
