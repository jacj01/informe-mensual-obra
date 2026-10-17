/* Navegacion accesible de pestanas (WAI-ARIA Tabs Pattern).
   Roving tabindex + flechas (izq/der/arriba/abajo), Home y End.
   La activacion dispara el .click() existente de cada pagina, por lo que
   no duplica la logica de cambio de panel. */
(function () {
  function initTablist(list) {
    var tabs = Array.prototype.slice.call(list.querySelectorAll('[role="tab"]'));
    if (!tabs.length) return;

    function setRoving(current) {
      tabs.forEach(function (t) {
        t.tabIndex = (t === current) ? 0 : -1;
      });
    }

    var active = tabs.filter(function (t) {
      return t.getAttribute('aria-selected') === 'true';
    })[0] || tabs[0];
    setRoving(active);

    function activate(tab) {
      tab.focus();
      if (tab.getAttribute('aria-selected') !== 'true') {
        tab.click();
      }
      setRoving(tab);
    }

    list.addEventListener('keydown', function (e) {
      var idx = tabs.indexOf(document.activeElement);
      if (idx === -1) return;
      var next = null;
      switch (e.key) {
        case 'ArrowRight':
        case 'ArrowDown':
          next = tabs[(idx + 1) % tabs.length]; break;
        case 'ArrowLeft':
        case 'ArrowUp':
          next = tabs[(idx - 1 + tabs.length) % tabs.length]; break;
        case 'Home':
          next = tabs[0]; break;
        case 'End':
          next = tabs[tabs.length - 1]; break;
        default:
          return;
      }
      e.preventDefault();
      activate(next);
    });

    list.addEventListener('click', function (e) {
      var tab = e.target.closest ? e.target.closest('[role="tab"]') : null;
      if (tab && tabs.indexOf(tab) !== -1) setRoving(tab);
    });
  }

  function initAll() {
    document.querySelectorAll('[role="tablist"]').forEach(initTablist);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }
})();
