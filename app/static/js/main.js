document.addEventListener('DOMContentLoaded', () => {

  // Evita múltiplos envios do formulário de login.
  const formularioLogin = document.querySelector('.login-form');

  if (formularioLogin) {
    formularioLogin.addEventListener('submit', () => {

      const botao = formularioLogin.querySelector(
        'button[type="submit"]'
      );

      if (botao) {
        botao.disabled = true;
        botao.textContent = 'Entrando...';
      }

    });
  }

  // Controle do menu responsivo do cabeçalho.
  const botaoMenu = document.getElementById('btn-menu-mobile');
  const menuHeader = document.getElementById('menu-header');
  if (botaoMenu && menuHeader) {
    const menuMobile = window.matchMedia('(max-width: 767px)');

    const fecharMenu = () => {
      menuHeader.classList.remove('menu-aberto');
      botaoMenu.setAttribute('aria-expanded', 'false');
      botaoMenu.setAttribute('aria-label', 'Abrir menu');
    };

    const alterarMenu = () => {
      const menuAberto = menuHeader.classList.toggle('menu-aberto');
      botaoMenu.setAttribute('aria-expanded', String(menuAberto));
      botaoMenu.setAttribute('aria-label', 
        menuAberto ? 'Fechar menu' : 'Abrir Menu'
      );
    };

    // Abre ou fecha menu pelo botão.
    botaoMenu.addEventListener('click', alterarMenu);

    // Fecha ao clicar em um link do menu.
    menuHeader.addEventListener('click', (evento) => {
      if (evento.target.closest('a')) {
        fecharMenu();
      }
    });

    // Fecha ao clicar fora do menu.
    document.addEventListener('click', (evento) => {
      if (
        !menuHeader.contains(evento.target) &&
        !botaoMenu.contains(evento.target)
      ) {
        fecharMenu();
      }
    });

    // Fechar ao pressionar 'ESC'.
    document.addEventListener('keydown', (evento) => {
      if (evento.key === 'Escape') {
        fecharMenu();
        botaoMenu.focus();
      }
    });

    // Fecha o menu ao mudar para um tela maior.
    menuMobile.addEventListener('change', (evento) => {
      if (!evento.matches) {
        fecharMenu();
      }
    });
  }

  // Controle do modo de alto contraste.
  const botaoContraste = document.getElementById('btn-alto-contraste');
  if (botaoContraste) {

    const aplicarAltoContraste = (ativado) => {
      document.body.classList.toggle('modo-alto-contraste', ativado);
      botaoContraste.setAttribute('aria-pressed', String(ativado));
      botaoContraste.textContent = ativado ? 'Desativar alto contraste' : 'Alto contraste';
    };

    // Recupera a preferência salva pelo usuário.
    let contrasteAtivado = false;

    try {
      contrasteAtivado =
        localStorage.getItem('altoContraste') === 'ativado';
    } catch (erro) {
      console.warn('Não foi possível recuperar a preferência de contraste.');
    }

    aplicarAltoContraste(contrasteAtivado);

    // Alterna o modo de contraste.
    botaoContraste.addEventListener('click', () => {

      contrasteAtivado = !contrasteAtivado;
      aplicarAltoContraste(contrasteAtivado);

      try {
        localStorage.setItem(
          'altoContraste',
          contrasteAtivado ? 'ativado' : 'desativado'
        );
      } catch (erro) {
        console.warn('Não foi possível salvar a preferência de contraste.');
      }
    });
  }
});
