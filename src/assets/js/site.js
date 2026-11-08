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

  // Rolagem: sombra no cabeçalho e botão flutuante depois da primeira tela (com um pulso na 1ª vez).
  var root = document.documentElement;
  var floatWa = document.querySelector('.float-wa');
  var pulsed = false;
  var onScroll = function () {
    var y = window.scrollY;
    root.classList.toggle('scrolled', y > 8);
    var show = y > window.innerHeight * 0.6;
    root.classList.toggle('show-float', show);
    if (show && !pulsed && floatWa) { pulsed = true; floatWa.classList.add('pulse'); }
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Entrada suave das seções, uma vez. Abaixo da dobra apenas; o que já está na tela fica parado.
  var calm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if ('IntersectionObserver' in window && !calm) {
    var els = document.querySelectorAll('.sec-head, .area, .about > *, .steps li, .callout > *, .faq, .cta-band, .prose > h2, .aside');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) {
      if (el.getBoundingClientRect().top > window.innerHeight) { el.classList.add('reveal'); io.observe(el); }
    });
    root.classList.add('reveal-ready');
  }

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
