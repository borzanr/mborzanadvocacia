// Menu do celular e formulário que monta a mensagem para o WhatsApp.
(function () {
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('menu');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
    });
  }

  // Botão flutuante aparece depois da primeira tela, para não cobrir os botões do topo.
  var root = document.documentElement;
  var onScroll = function () { root.classList.toggle('show-float', window.scrollY > window.innerHeight * 0.6); };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  var form = document.getElementById('form-contato');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = form.elements;
      var linhas = [
        'Olá, Dr. Mauro! Vim pelo site.',
        'Nome: ' + f.nome.value.trim(),
        'Assunto: ' + f.area.value,
        f.cidade.value.trim() ? 'Cidade: ' + f.cidade.value.trim() : '',
        '',
        f.mensagem.value.trim()
      ].filter(function (l, i) { return l !== '' || i === 4; });
      var url = 'https://wa.me/' + form.dataset.phone + '?text=' + encodeURIComponent(linhas.join('\n'));
      window.open(url, '_blank', 'noopener');
    });
  }
})();
