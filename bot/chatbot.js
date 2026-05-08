
'use strict';

/* ── ESTADO GLOBAL ── */
const state = {
  conversations:  [],   // lista de conversas
  activeConvId:   null, // id da conversa selecionada
  convMessages:   {},   // { [convId]: [] } — mensagens por conversa
  convQuoteItems: {},   // { [convId]: [] } — itens de orçamento por conversa
  menuOpen:       false,
  convCounter:    0,    // contador de conversas criadas
  quoteCounter:   0,    // contador de itens criados
  deletedConvs:   {},   // — lixeira temporária
  modoOrcamento: false,
  etapaOrcamento: null,
  dadosOrcamento:{}
};

/* Atalhos para acessar dados da conversa ativa */
function activeMessages()   { return state.convMessages[state.activeConvId]   || []; }
function activeQuoteItems() { return state.convQuoteItems[state.activeConvId] || []; }

/* ════════════════════════════════════════════════
   UTILITÁRIOS
════════════════════════════════════════════════ */

/** Hora atual formatada HH:MM */
function now() {
  return new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

/** Data amigável relativa */
function dateStr(timestamp) {
  const diff = Date.now() - timestamp;
  if (diff < 60_000)      return 'Agora';
  if (diff < 3_600_000)   return Math.floor(diff / 60_000) + 'min atrás';
  return new Date(timestamp).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
}

  /* ******************************************************************************* */
 /* *************************** async que irão retornar os valores do banco ********************************* */
  /* ******************************************************************************* */

////////////////// insumos ///////////////////////////////////

async function buscarPorCategoria(categoria){
  const response = await fetch(`http://127.0.0.1:5000/insumos?categoria=${categoria}`);
  const data = await response.json();

  if(!data.length) {
    return "Nenhum insumo encontrado."
  }
  
  let resposta = " Itens encontrados:\n\n";

  data.forEach(i => {
    resposta += 
    ` ${i.modelo || i.categoria} \n` +
    ` - Preço: R$ ${i.preco_venda || i.preco_unitario}\n` +
    ` - Estoque: ${i.estoque_disponivel} ${i.unidade_medida || ""} \n\n`
  });

  return resposta;
}
/////////////////////////////////////////////////////////////

////////////////// orçamentos ///////////////////////////////////
async function enviarOrcamentoParaAPI(dados) {
  const response = await fetch("http://127.0.0.1:5000/orcamentos", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(dados)
  })

  return await response.json();
}


async function tratarFluxoOrcamento(text){
  if(state.etapaOrcamento === "categoria"){
    state.dadosOrcamento.categoria = text;
    state.etapaOrcamento = "quantidade_convites";
    addBotMessage("Informe a quantidade de convites:");
    return;
  }

  if(state.etapaOrcamento === "quantidade_convites") {
    state.dadosOrcamento.quantidade_convites = Number(text);
    state.etapaOrcamento = "largura_folha";
    addBotMessage("Informe a largura da folha:");
    return;
  }

  if(state.etapaOrcamento === "largura_folha") {
    state.dadosOrcamento.largura_folha = Number(text);
    state.etapaOrcamento = "altura_folha";
    addBotMessage("Informe a altura da folha");
    return;
  }

  if (state.etapaOrcamento === "altura_folha") {
    state.dadosOrcamento.altura_folha = Number(text);
    state.etapaOrcamento = "largura_impressao";
    addBotMessage("Informe a largura da impressão:");
    return;
  }


  if(state.etapaOrcamento === "largura_impressao") {
    state.dadosOrcamento.largura_impressao = Number(text);
    state.etapaOrcamento = "altura_impressao";
    addBotMessage("Informe a altura da impressão:");
    return;
  }

  if(state.etapaOrcamento === "altura_impressao") {
    state.dadosOrcamento.altura_impressao = Number(text);

    state.dadosOrcamento.margem = 1.0;
    state.dadosOrcamento.sangria = 0.2;
    state.dadosOrcamento.margem_lucro = 30;

    const resultado = await enviarOrcamentoParaAPI(state.dadosOrcamento);

    if(resultado.erro) {
      addBotMessage(`${resultado.erro}`);
    } else {
      const valor = Number(resultado.orcamento.valor_final).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL"
      });

      addBotMessage(
        `📄 Orçamento calculado:\n\n` +
        `📦 Aproveitamento: ${resultado.orcamento.aproveitamento}\n` +
        `📄 Folhas necessárias: ${resultado.orcamento.folhas_necessarias}\n` +
        `💰 Custo total: R$ ${resultado.orcamento.custo_total}\n` +
        `💵 Valor final: ${valor}\n` +
        `📦 Estoque restante: ${resultado.orcamento.estoque_restante}`
      );
    }

    state.modoOrcamento = false;
    state.etapaOrcamento = null;
    state.dadosOrcamento = {};

  }

}

/////////////////////////////////////////////////////////////////


/***********************************************************************************************/
/***********************************************************************************************/
/***********************************************************************************************/


/* ════════════════════════════════════════════════
   MENU LATERAL (SIDEBAR)
════════════════════════════════════════════════ */

function toggleMenu() {
  state.menuOpen = !state.menuOpen;
  document.getElementById('menuSidebar').classList.toggle('open',    state.menuOpen);
  document.getElementById('overlay').classList.toggle('visible',     state.menuOpen);
  document.getElementById('menuToggleBtn').classList.toggle('active', state.menuOpen);
}

/* ════════════════════════════════════════════════
   CONVERSAS
════════════════════════════════════════════════ */

/** Cria uma nova conversa e a define como ativa */
function newConversation() {
  state.convCounter++;

  const conv = {
    id:        state.convCounter,
    name:      'Conversa ' + state.convCounter,
    createdAt: Date.now(),
    msgCount:  0,
    active:    true,
  };

  state.conversations.unshift(conv);
  state.activeConvId = conv.id;
  state.convMessages[conv.id]   = [];
  state.convQuoteItems[conv.id] = [];

  renderConvList();
  renderMessages();
  renderQuotePanel();
  updateFooter();
  updateFinishBtn(true);

  addBotMessage(
    'Olá! 👋 Sou o Assistente Virtual da Lamore!\n\n' +
    'Estou aqui para ajudar você a gerenciar nossos produtos!\n\n' +
    '📋 Comandos disponíveis:\n' +
    '• "buscar [nome]" – procurar produtos\n' +
    '• "estoque(código)" – ver estoque\n' +
    '• "categoria(tipo)" – listar por categoria\n' +
    '• "pedido novo" – criar novo pedido\n' +
    '• "preço(código)" – consultar preço\n' +
    '• "ajuda" – ver todos os comandos\n' +
    '• "Ver Produtos\n\n' +
    'O que você precisa hoje?'
  );
}

/** Seleciona uma conversa existente e carrega seus dados */
function selectConv(id) {
  state.activeConvId = id;
  renderConvList();
  renderMessages();
  renderQuotePanel();
  updateFooter();
  const conv = state.conversations.find(c => c.id === id);
  if (conv) updateFinishBtn(conv.active);
}

/** Exclui uma conversa com opção de reverter via toast */
function deleteConv(id, event) {
  event.stopPropagation();

  const idx = state.conversations.findIndex(c => c.id === id);
  if (idx === -1) return;

  const conv = state.conversations[idx];

  state.deletedConvs[id] = {
    conv,
    index:      idx,
    messages:   state.convMessages[id]   || [],
    quoteItems: state.convQuoteItems[id] || [],
  };

  state.conversations.splice(idx, 1);
  delete state.convMessages[id];
  delete state.convQuoteItems[id];

  if (state.activeConvId === id) {
    const next = state.conversations[0];
    state.activeConvId = next ? next.id : null;
  }

  renderConvList();
  renderMessages();
  renderQuotePanel();
  updateFooter();
  showDeleteToast(id, conv.name);
}

/** Reverte a exclusão de uma conversa */
function undoDelete(id) {
  const saved = state.deletedConvs[id];
  if (!saved) return;

  const insertAt = Math.min(saved.index, state.conversations.length);
  state.conversations.splice(insertAt, 0, saved.conv);
  state.convMessages[id]   = saved.messages;
  state.convQuoteItems[id] = saved.quoteItems;

  delete state.deletedConvs[id];

  state.activeConvId = id;
  renderConvList();
  renderMessages();
  renderQuotePanel();
  updateFooter();
  hideDeleteToast();
}

function showDeleteToast(id, name) {
  hideDeleteToast();

  const toast = document.createElement('div');
  toast.id        = 'deleteToast';
  toast.className = 'delete-toast';
  toast.innerHTML = `
    <span>Conversa "<strong>${name}</strong>" excluída.</span>
    <button class="toast-undo-btn" onclick="undoDelete(${id})">Desfazer</button>
    <div class="toast-progress" id="toastProgress"></div>
  `;
  document.body.appendChild(toast);

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      const bar = document.getElementById('toastProgress');
      if (bar) bar.style.width = '0%';
    });
  });

  state._toastTimer = setTimeout(() => {
    hideDeleteToast();
    delete state.deletedConvs[id];
  }, 5000);
}

function hideDeleteToast() {
  clearTimeout(state._toastTimer);
  const old = document.getElementById('deleteToast');
  if (old) old.remove();
}

/** Renomeia uma conversa */
function renameConv(id, newName) {
  const conv = state.conversations.find(c => c.id === id);
  if (conv && newName.trim()) conv.name = newName.trim();
  renderConvList();
}

/** Alterna o status ativo/encerrado da conversa selecionada */
function toggleActive() {
  const conv = state.conversations.find(c => c.id === state.activeConvId);
  if (conv) {
    conv.active = !conv.active;
    updateFooter();
    updateFinishBtn(conv.active);
  }
}

/** Atualiza o visual do botão "Finalizar conversa" na área do chat */
function updateFinishBtn(isActive) {
  const btn   = document.getElementById('finishConvBtn');
  const label = document.getElementById('finishConvLabel');
  if (!btn || !label) return;

  if (isActive) {
    btn.className   = 'finish-conv-btn';
    label.textContent = 'Finalizar conversa';
    btn.querySelector('svg').innerHTML = '<polyline points="20 6 9 17 4 12"/>';
  } else {
    btn.className   = 'finish-conv-btn reopen';
    label.textContent = 'Reabrir conversa';
    btn.querySelector('svg').innerHTML = '<path d="M3 12a9 9 0 109 9"/><polyline points="3 7 3 12 8 12"/>';
  }
}

/* Abrir o menu usuário, deslogar TERMINAR */

/* Filtro de pesquisa TERMINAR */
function filterConversations() {
  const searchTerm = document.getElementById('search-container input').value.toLowerCase();
  const convItems = document.querySelectorAll('.conv-item');

  convItems.forEach(item => {
    const title = item.querySelector('.conv-title').innerText.toLowerCase();
    if (title.includes(searchTerm)) {
      item.style.display = 'flex';
    } else {
      item.style.display = 'none';
    }
  });
}

/* ════════════════════════════════════════════════
   RENDERIZAÇÃO — LISTA DE CONVERSAS
════════════════════════════════════════════════ */

function renderConvList() {
  const list = document.getElementById('convList');
  list.innerHTML = '';

  if (!state.conversations.length) {
    list.innerHTML = '<div style="font-size:12px;color:var(--gray-400);text-align:center;padding:12px 0">Nenhuma conversa ainda</div>';
    return;
  }

  state.conversations.forEach(conv => {
    const card = document.createElement('div');
    card.className = 'conv-card' + (conv.id === state.activeConvId ? ' active-conv' : '');
    card.onclick = () => selectConv(conv.id);

    card.innerHTML = `
      <div class="conv-card-top">
        <input
          class="conv-name-input"
          value="${conv.name}"
          onclick="event.stopPropagation()"
          onblur="renameConv(${conv.id}, this.value)"
          onkeydown="if(event.key==='Enter') this.blur()">
        <button
          class="conv-delete-btn"
          title="Excluir conversa"
          onclick="deleteConv(${conv.id}, event)">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
            <path d="M10 11v6M14 11v6"/>
            <path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/>
          </svg>
        </button>
      </div>

      <div class="conv-meta">
        <span class="conv-badge">${conv.msgCount} Msg ${conv.msgCount !== 1 ? 's' : ''}</span>
        <span class="conv-date">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          ${dateStr(conv.createdAt)}
        </span>
      </div>
    `;

    list.appendChild(card);
  });
}

/** Atualiza rodapé: total de conversas + status ativa */
function updateFooter() {
  document.getElementById('totalConvs').textContent = state.conversations.length;

  const conv = state.conversations.find(c => c.id === state.activeConvId);
  const btn  = document.getElementById('activeToggle');

  if (!conv) {
    btn.textContent = '—';
    btn.className   = 'status-toggle';
    return;
  }

  btn.textContent = conv.active ? 'Sim' : 'Não';
  btn.className   = 'status-toggle ' + (conv.active ? 'sim' : 'nao');
}


/* ════════════════════════════════════════════════
   MENSAGENS
════════════════════════════════════════════════ */

/** Adiciona mensagem do bot */
function addBotMessage(text) {
  const conv = state.conversations.find(c => c.id === state.activeConvId);
  if (!conv) return;
  conv.msgCount++;
  if (!state.convMessages[conv.id]) state.convMessages[conv.id] = [];
  state.convMessages[conv.id].push({ type: 'bot', text, time: now() });
  renderMessages();
  renderConvList();
}

/** Adiciona mensagem do usuário */
function addUserMessage(text) {
  const conv = state.conversations.find(c => c.id === state.activeConvId);
  if (!conv) return;
  conv.msgCount++;
  if (!state.convMessages[conv.id]) state.convMessages[conv.id] = [];
  state.convMessages[conv.id].push({ type: 'user', text, time: now() });
  renderMessages();
  renderConvList();
}

/** Renderiza todas as mensagens no DOM */
function renderMessages() {
  const container = document.getElementById('messages');
  container.innerHTML = '';

  const msgs = activeMessages();

  if (!msgs.length && !state.activeConvId) {
    container.innerHTML = '<div style="text-align:center;color:var(--gray-400);font-size:13px;margin-top:40px">Selecione ou crie uma conversa.</div>';
    return;
  }

  msgs.forEach(msg => {
    const row = document.createElement('div');
    row.className = 'msg-row ' + msg.type;

    const safe = msg.text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    if (msg.type === 'bot') {
    row.innerHTML = `
    <img src="../images/french-bulldog.png" alt="L'amore Bot" class="msg-avatar" onerror="this.style.display='none'">
    <div>
      <div class="msg-bubble bot">${safe}<div class="msg-time">${msg.time}</div></div>
    </div>`;

} else {
  row.innerHTML = `
    <div class="msg-bubble user">${safe}<div class="msg-time">${msg.time}</div></div>`;
}

    container.appendChild(row);
  });

  container.scrollTop = container.scrollHeight;
}


/** Preenche o campo de texto com um atalho rápido */
function insertShortcut(cmd) {
  const input = document.getElementById('chatInput');
  input.value = cmd;
  input.focus();
}


/* ════════════════════════════════════════════════
   LÓGICA DE RESPOSTAS DO BOT
════════════════════════════════════════════════ */

const BOT_RESPONSES = {
  'ajuda': () =>
    'Comandos disponíveis:\n' +
    '• "Insumo (nome do insumo)" – procurar produto\n' +
    '• "pedido novo" – criar pedido\n' +
    '• "estoque(código)" – verificar estoque\n' +
    '• "categoria(tipo)" – listar categoria\n' +
    '• "preço(código)" – consultar preço\n' +
    '• "resumo" – ver itens do orçamento\n' +
    '• "convites" – listar convites',

  'resumo': () =>
    activeQuoteItems().length
      ? `Seu orçamento tem ${activeQuoteItems().length} item(ns). Confira no painel ao lado.`
      : 'Seu orçamento está vazio. Use "pedido novo" para adicionar itens.',
      
  'produtos': () => {
    addQuoteItem('Convite Clássico', 'Papel A4', 'Esmeralda', 500, 'conv-' + (state.quoteCounter + 1));
    return 'Listando convites disponíveis! Adicionei um item de exemplo ao orçamento.';
  },


  /* FUNÇÃO DE PEDIDO NOVO */
  'pedido novo': () => {
    state.modoOrcamento = true;
    state.etapaOrcamento = "categoria";
    state.dadosOrcamento = {};

    return "Vamos criar um orçamento. Informe a categoria do insumo:";
  },
  
  'default': (input) => {
    if (input.startsWith('buscar ')) {
      const term = input.replace('buscar ', '');
      addQuoteItem('Produto: ' + term, 'Papel A4', 'Personalizado', 50, 'conv-' + (state.quoteCounter + 1));
      return `Busquei por "${term}". Um item foi adicionado ao orçamento para sua revisão.`;
    }
    if (input.startsWith('preço(')) {
      return `Preço do produto ${input}: R$ 2,50/unidade (pedido mínimo 50 unidades).`;
    }
    return 'Não reconheci o comando. Digite "ajuda" para ver os comandos disponíveis.';
  },
};

  /* ******************************************************************************* */
 /* *************************** Inputs do Usuario ********************************* */
  /* ******************************************************************************* */
    async function getBotReply(input) {
    const text = input.toLowerCase().trim();

    if (text.startsWith("insumos") || text.startsWith("insumo")) {
      const partes = text.split(" ");
      const categoria = partes[1]; // pode ser undefined

      return await buscarPorCategoria(categoria);
    }

    if (BOT_RESPONSES[text]) {
      return await BOT_RESPONSES[text]();
    }

    return BOT_RESPONSES['default'](text);

  }

  /* ******************************************************************************* */
  /* ******************************************************************************* */
  /* ******************************************************************************* */


/** Envia a mensagem do usuário e aciona a resposta do bot */
function sendMessage() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;

  if (!state.activeConvId) newConversation();

  input.value = '';
  addUserMessage(text);

  // 🔥 fluxo de orçamento
  if (state.modoOrcamento) {
    tratarFluxoOrcamento(text);
    return;
  }

  // resposta normal do bot
  setTimeout(async () => {
    const resposta = await getBotReply(text);
    addBotMessage(resposta);
  }, 600);
}

/** Envia a mensagem do usuário e aciona a resposta do bot */

/* ════════════════════════════════════════════════
   PAINEL DE ORÇAMENTO
════════════════════════════════════════════════ */

/** Adiciona novo item de orçamento na conversa ativa */
function addQuoteItem(title, papel, cor, qty, code) {
  if (!state.activeConvId) return;
  state.quoteCounter++;
  if (!state.convQuoteItems[state.activeConvId]) state.convQuoteItems[state.activeConvId] = [];
  state.convQuoteItems[state.activeConvId].unshift({
    id: state.quoteCounter,
    title, papel, cor, qty, code,
    status: 'pendente',
  });
  renderQuotePanel();
}

/** Confirma um item no orçamento */
function confirmItem(id) {
  const item = activeQuoteItems().find(i => i.id === id);
  if (item) { item.status = 'concluido'; renderQuotePanel(); }
}

/** Exclui (marca como excluído) um item do orçamento */
function removeItem(id) {
  const item = activeQuoteItems().find(i => i.id === id);
  if (item) { item.status = 'excluido'; renderQuotePanel(); }
}

/** Renderiza todos os cards do orçamento da conversa ativa */
function renderQuotePanel() {
  const panel = document.getElementById('quoteItems');
  const items = activeQuoteItems();

  if (!items.length) {
    panel.innerHTML = `
      <div style="text-align:center; color:var(--gray-400); font-size:12px; margin-top:24px; line-height:1.8;">
        Nenhum item ainda.<br>Use o chat para adicionar produtos ao orçamento.
      </div>`;
    return;
  }

  panel.innerHTML = '';

  items.forEach(item => {
    const LABELS   = { concluido: 'Concluído', excluido: 'Excluído', pendente: 'Pendente' };
    const BADGES   = { concluido: 'badge-ok',  excluido: 'badge-excluido', pendente: 'badge-pendente' };
    const statusOk = item.status !== 'excluido';
    const icon     = statusOk ? '✓' : '✗';
    const iconCls  = statusOk ? 'ok-icon' : 'no-icon';

    let actions = '';
    if (item.status === 'pendente') {
      actions = `
        <button class="quote-action-btn confirm" onclick="confirmItem(${item.id})">Confirmar</button>
        <button class="quote-action-btn remove"  onclick="removeItem(${item.id})">Excluir</button>`;
    } else if (item.status === 'excluido') {
      actions = `<button class="quote-action-btn" onclick="confirmItem(${item.id})">Restaurar</button>`;
    } else {
      actions = `<button class="quote-action-btn remove" onclick="removeItem(${item.id})">Remover</button>`;
    }

    const card = document.createElement('div');
    card.className = 'quote-card';
    card.innerHTML = `
      <div class="quote-card-header">
        <span class="quote-tag">Convites</span>
        <span class="quote-status-badge ${BADGES[item.status]}">${LABELS[item.status]}</span>
      </div>
      <div class="quote-card-body">
        <div class="quote-title">${item.title}</div>
        <div class="quote-detail"><span class="${iconCls}">${icon}</span> ${item.papel}</div>
        <div class="quote-detail"><span class="${iconCls}">${icon}</span> Cor ${item.cor}</div>
        <div class="quote-detail"><span class="${iconCls}">${icon}</span> Quantidade: ${item.qty}</div>
        <div class="status-label ${item.status}">
          ${item.status === 'pendente' ? 'Aguardando...' : LABELS[item.status]}
        </div>
      </div>
      <div class="quote-card-actions">${actions}</div>
      <div class="quote-code">Código ${item.code}-00${item.id}</div>
    `;

    panel.appendChild(card);
  });
}


/* ════════════════════════════════════════════════
   INICIALIZAÇÃO
════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  newConversation();
});

