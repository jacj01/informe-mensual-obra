// Utilidades del aplicativo Informe Financiero
document.addEventListener('DOMContentLoaded', function () {
  // Auto-ocultar alertas después de 4 segundos
  document.querySelectorAll('.alert').forEach(function (a) {
    setTimeout(function () {
      a.style.transition = 'opacity .4s';
      a.style.opacity = '0';
      setTimeout(function () { a.remove(); }, 400);
    }, 4000);
  });
});
