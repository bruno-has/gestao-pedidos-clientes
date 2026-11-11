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
