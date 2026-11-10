document.addEventListener("DOMContentLoaded", () => {
  const listaItens = document.getElementById("lista-itens");
  const btnAdicionar = document.getElementById("btn-adicionar-item");
  const valorTotal = document.getElementById("valor-total");

  // Atualiza o valor total do pedido
  function calcularTotal() {
    let total = 0;

    const itens = listaItens.querySelectorAll(".pedido-item");

    itens.forEach((item) => {
      const quantidade = Number(
        item.querySelector('[name="quantidade[]"]').value,
      );

      const valor = Number(
        item.querySelector('[name="valor_unitario[]"]').value,
      );

      if (
        Number.isFinite(quantidade) &&
        Number.isFinite(valor) &&
        quantidade > 0 &&
        valor > 0
      ) {
        total += quantidade * valor;
      }
    });

    valorTotal.textContent = total.toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  }

  // Adiciona um novo item ao pedido
  function adicionarItem() {
    const novoItem = document.createElement("div");

    novoItem.classList.add("pedido-item");

    novoItem.innerHTML = `
      <div class="pedido-campo produto-campo">
        <label>Produto</label>
        <input
          type="text"
          name="nome_produto[]"
          placeholder="Ex.: Bolo de chocolate"
          maxlength="100"
          required
        >
      </div>

      <div class="pedido-campo quantidade-campo">
        <label>Quantidade</label>
        <input
          type="number"
          name="quantidade[]"
          min="1"
          step="1"
          value="1"
          required
        >
      </div>

      <div class="pedido-campo valor-campo">
        <label>Valor unitário (R$)</label>
        <input
          type="number"
          name="valor_unitario[]"
          min="0.01"
          step="0.01"
          placeholder="0,00"
          required
        >
      </div>

      <button
        type="button"
        class="btn-remover-item"
        aria-label="Remover item"
        title="Remover item"
      >Remover</button>
    `;

    listaItens.appendChild(novoItem);

    calcularTotal();
  }

  // Eventos dos botões e campos
  btnAdicionar.addEventListener("click", adicionarItem);

  listaItens.addEventListener("click", (evento) => {
    if (evento.target.classList.contains("btn-remover-item")) {
      const itens = listaItens.querySelectorAll(".pedido-item");

      // Mantém pelo menos um item no formulário
      if (itens.length > 1) {
        evento.target.closest(".pedido-item").remove();
        calcularTotal();
      }
    }
  });

  listaItens.addEventListener("input", calcularTotal);

  // Calcula o total inicial
  calcularTotal();
});
