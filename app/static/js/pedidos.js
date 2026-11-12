document.addEventListener("DOMContentLoaded", () => {
  const listaItens = document.getElementById("lista-itens");
  const btnAdicionar = document.getElementById("btn-adicionar-item");
  const valorTotal = document.getElementById("valor-total");

  if (!listaItens || !btnAdicionar || !valorTotal) {
    return;
  }

  // Obtém o valor unitário do produto selecionado.
  function obterValorProduto(item) {
    const select = item.querySelector('[name="produto_id[]"]');
    if (!select || select.selectedIndex < 0) {
      return 0;
    }

    const opcao = select.options[select.selectedIndex];

    return Number(opcao.dataset.valor || 0);
  }

  // Atualiza a exibição do valor unitário.
  function atualizarValorUnitario(item) {
    const valorExibicao = item.querySelector(".valor_unitario_exibicao");
    if (!valorExibicao) {
      return;
    }

    const valor = obterValorProduto(item);

    if (valor > 0) {
      valorExibicao.textContent =
        "Valor unitário: " +
        valor.toLocaleString("pt-BR", {
          style: "currency",
          currency: "BRL",
        });
    } else {
      valorExibicao.textContent = "Selecione um produto";
    }
  }

  // Calcula o valor total de todos os itens.
  function calcularTotal() {
    let total = 0;

    const itens = listaItens.querySelectorAll(".pedido-item");
    itens.forEach((item) => {
      const campoQuantidade = item.querySelector('[name="quantidade[]"]');
      if (!campoQuantidade) {
        return;
      }

      const quantidade = Number(campoQuantidade.value);
      const valor = obterValorProduto(item);

      if (
        Number.isFinite(quantidade) &&
        Number.isFinite(valor) &&
        quantidade > 0 &&
        valor > 0
      ) {
        total += quantidade * valor;
      }

      atualizarValorUnitario(item);
    });

    valorTotal.textContent = total.toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  }

  // Adiciona uma nova linha de produto.
  function adicionarItem() {
    const primeiroItem = listaItens.querySelector(".pedido-item");
    if (!primeiroItem) {
      return;
    }

    const novoItem = primeiroItem.cloneNode(true);

    const select = novoItem.querySelector('[name="produto_id[]"]');
    const quantidade = novoItem.querySelector('[name="quantidade[]"]');

    if (!select || !quantidade) {
      return;
    }

    select.selectedIndex = 0;
    quantidade.value = 1;

    listaItens.appendChild(novoItem);

    calcularTotal();
  }

  // Evento do botão adicionar.
  btnAdicionar.addEventListener("click", adicionarItem);

  // Detecta a seleção ou alteração do produto.
  listaItens.addEventListener("change", (evento) => {
    if (evento.target.matches('[name="produto_id[]"]')) {
      calcularTotal();
    }
  });

  // Detecta alterações na quantidade.
  listaItens.addEventListener("input", (evento) => {
    if (evento.target.matches('[name="quantidade[]"]')) {
      calcularTotal();
    }
  });

  // Remove um item do pedido.
  listaItens.addEventListener("click", (evento) => {
    if (evento.target.closest(".btn-remover-item")) {
      const itens = listaItens.querySelectorAll(".pedido-item");

      if (itens.length > 1) {
        evento.target.closest(".pedido-item").remove();
        calcularTotal();
      }
    }
  });

  // Calcula o total inicial ao carregar a página.
  calcularTotal();
});
