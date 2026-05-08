// Estado global para controlar o menu
const state = {
    menuOpen: false
};

function toggleMenu() {
    state.menuOpen = !state.menuOpen;
    const menu = document.getElementById('menuSidebar');
    const overlay = document.getElementById('overlay');
    const btn = document.getElementById('menuToggleBtn');

    if (menu) menu.classList.toggle('open', state.menuOpen);
    if (overlay) overlay.classList.toggle('visible', state.menuOpen);
    if (btn) btn.classList.toggle('active', state.menuOpen);
}

const produtos = [
    { id: 1, nome: "Produto 1", qtd: 69, valor: 100 },
    { id: 2, nome: "Produto 2", qtd: 67, valor: 400 },
    { id: 3, nome: "Produto 3", qtd: 10, valor: 30 },
    { id: 4, nome: "Produto 4", qtd: 24, valor: 20 },
    { id: 5, nome: "Produto 5", qtd: 6, valor: 40 },
    { id: 6, nome: "Produto 6", qtd: 7, valor: 500 },
    { id: 7, nome: "Produto 7", qtd: 9, valor: 10 },
    { id: 8, nome: "Produto 8", qtd: 11, valor: 70 },
    { id: 9, nome: "Produto 9", qtd: 5, valor: 60 },
    { id: 10, nome: "Produto 10", qtd: 3, valor: 90 },
    { id: 11, nome: "Produto 11", qtd: 15, valor: 120 },
    { id: 12, nome: "Produto 12", qtd: 2, valor: 55 },
    { id: 13, nome: "Produto 13", qtd: 35, valor: 33},
    { id: 14, nome: "Produto 14", qtd: 79, valor: 83},
    { id: 15, nome: "Produto 15", qtd: 90, valor: 330},
    { id: 16, nome: "Produto 16", qtd: 105, valor: 133},
    { id: 17, nome: "Produto 17", qtd: 305, valor: 233},
    { id: 18, nome: "Produto 18", qtd: 300, valor: 10},
    { id: 19, nome: "Produto 19", qtd: 100, valor: 100},
    { id: 20, nome: "Produto 20", qtd: 135, valor: 333},
    { id: 21, nome: "Produto 21", qtd: 10, valor: 400},
    { id: 22, nome: "Produto 22", qtd: 1, valor: 3},
    { id: 23, nome: "Produto 23", qtd: 15, valor: 400},
    { id: 24, nome: "Produto 24", qtd: 40, valor: 200},
    { id: 25, nome: "Produto 25", qtd: 200, valor: 25}
];

let paginaAtual = 1;
const itensPorPagina = 10;
let produtosFiltrados = [...produtos]; // Começa com todos

function mostrarProdutos() {
    const container = document.getElementById("productList");
    container.innerHTML = "";

    const inicio = (paginaAtual - 1) * itensPorPagina;
    const fim = inicio + itensPorPagina;
    const produtosPagina = produtosFiltrados.slice(inicio, fim);

    produtosPagina.forEach(produto => {

        const podeExcluir = (typeof USER_ROLE !== "undefined" && USER_ROLE === "admin");

        container.innerHTML += `
        <div class="row">
            <span>${produto.id}</span>
            <span>${produto.nome}</span>
            <span>${produto.qtd}</span>
            <span>R$ ${produto.valor.toFixed(2)}</span>
            ${podeExcluir ? `<button class="btn-delete" onclick="excluirProduto(${produto.id})">🗑️</button>` : ''}
        </div>`;
    });
}
// excluir
function excluirProduto(id) {

    if (USER_ROLE !== "admin") {
        alert("Você não tem permissão para excluir!");
        return;
    }

    const confirmar = confirm("Tem certeza que deseja excluir este produto?");
    if (!confirmar) return;

    // Remove do array principal
    const index = produtos.findIndex(p => p.id === id);
    if (index !== -1) {
        produtos.splice(index, 1);
    }

    // Atualiza lista filtrada
    produtosFiltrados = produtos;

    mostrarProdutos();
}

function irParaPagina(numero) {
    paginaAtual = numero;
    atualizarBotoes();
    mostrarProdutos();
}

function proximaPagina() {
    const totalPaginas = Math.ceil(produtosFiltrados.length / itensPorPagina);
    if (paginaAtual < totalPaginas) {
        paginaAtual++;
        atualizarBotoes();
        mostrarProdutos();
    }
}

function paginaAnterior() {
    if (paginaAtual > 1) {
        paginaAtual--;
        atualizarBotoes();
        mostrarProdutos();
    }
}

function atualizarBotoes() {
    const botoes = document.querySelectorAll(".page-number");
    botoes.forEach((btn, index) => {
        if (index === paginaAtual - 1) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });
}

function pesquisarProduto() {
    const texto = document.getElementById("searchInput").value.toLowerCase();
    
    produtosFiltrados = produtos.filter(produto =>
        produto.nome.toLowerCase().includes(texto)
    );

    paginaAtual = 1; // Reseta para a primeira página na busca
    atualizarBotoes();
    mostrarProdutos();
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    mostrarProdutos();

    console.log("ROLE NO LOAD:", USER_ROLE);

    if (USER_ROLE !== "admin") {
        const btn = document.getElementById("btnEditar");
        if (btn) btn.style.display = "none";
    }
});




// NOVA FUNÇÃO: Transforma a tabela em campos editáveis
function habilitarEdicaoGeral() {

    console.log("ROLE:", USER_ROLE); // DEBUG

    if (typeof USER_ROLE === "undefined" || USER_ROLE !== "admin") {
        alert("Você não tem permissão para editar!");
        return;
    }

    const rows = document.querySelectorAll("#productList .row");
    
    rows.forEach((row) => {
        const spans = row.querySelectorAll("span");

        const nomeAtual = spans[1].innerText;
        const qtdAtual = spans[2].innerText;
        const valorAtual = spans[3].innerText.replace("R$ ", "");

        spans[1].innerHTML = `<input class="edit-input" type="text" value="${nomeAtual}">`;
        spans[2].innerHTML = `<input class="edit-input" type="number" value="${qtdAtual}">`;
        spans[3].innerHTML = `<input class="edit-input" type="number" step="0.01" value="${valorAtual}">`;
    });

    // 🔥 GARANTE QUE O BOTÃO SEMPRE APAREÇA
    let btn = document.getElementById("btnSalvarGeral");

    if (!btn) {
        btn = document.createElement("button");
        btn.id = "btnSalvarGeral";
        btn.innerText = "SALVAR ALTERAÇÕES";
        btn.className = "save-all-btn";
        btn.onclick = salvarTodasAlteracoes;
        document.querySelector(".products-box").appendChild(btn);
    }

    btn.style.display = "block"; // 🔥 força aparecer
}
// NOVA FUNÇÃO: Salva os dados dos inputs de volta para o array 'produtos'
function salvarTodasAlteracoes() {
    const rows = document.querySelectorAll("#productList .row");
    
    rows.forEach(row => {
        const id = parseInt(row.querySelector("span:nth-child(1)").innerText);
        const inputs = row.querySelectorAll("input");
        
        // Localiza o produto no seu array original pelo ID
        const produto = produtos.find(p => p.id === id);
        
        if (produto) {
            produto.nome = inputs[0].value;
            produto.qtd = parseInt(inputs[1].value);
            produto.valor = parseFloat(inputs[2].value);
        }
    });

    alert("Todos os produtos foram atualizados com sucesso!");
    
    // Remove o botão de salvar e redesenha a tabela usando sua função original
    document.getElementById("btnSalvarGeral").remove();
    mostrarProdutos(); 
}


