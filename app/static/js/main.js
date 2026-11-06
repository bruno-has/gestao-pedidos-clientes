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
});
