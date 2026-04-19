/* --- ESTADO DOS DADOS --- */
// Centralizamos as informações no array 'conversas' que você já utiliza
let conversas = [
    {
        id: 1,
        nome: "Orçamento Maria",
        data: "Hoje",
        ativa: true,
        mensagens: [
            { tipo: 'bot', texto: "Olá! 👋 Sou o Assistente da Lamore. Como posso ajudar?", hora: "09:10" },
            { tipo: 'user', texto: "Pedido de 500 convites.", hora: "09:12" }
        ],
        itensOrcamento: [{ status: 'Concluído', texto: 'Convite A4 (500 un)', tipo: 'green', cod: 'conv-001' }]
    }
];

let idAtivo = 1;

/**
 * Captura o texto do input e adiciona à conversa ativa
 */
function sendMessage() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    
    // Encontra a conversa que está aberta no momento
    const chatAtual = conversas.find(c => c.id === idAtivo);

    if (text !== "" && chatAtual) {
        // 1. Adiciona a mensagem do usuário ao array de mensagens daquela conversa
        chatAtual.mensagens.push({
            tipo: 'user',
            texto: text,
            hora: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
        });

        // 2. Limpa o campo de entrada
        input.value = "";

        // 3. Atualiza a tela imediatamente
        renderizar();

        // 4. Simulação de resposta do bot para teste estético
        setTimeout(() => {
            chatAtual.mensagens.push({
                tipo: 'bot',
                texto: "Entendido! Estou processando as informações sobre: " + text,
                hora: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
            });
            renderizar();
        }, 800);
    }
}

/**
 * Alterna a visibilidade do menu lateral
 */
function toggleMenu() {
    const menu = document.getElementById('sideMenu');
    if (menu) {
        menu.style.display = (menu.style.display === 'flex') ? 'none' : 'flex';
    }
}

/**
 * Troca a conversa ativa e atualiza a interface
 */
function mudarConversa(id) {
    idAtivo = id;
    renderizar();
}

/**
 * Função de Renderização Principal
 * Atualiza o histórico, o chat e o orçamento lateral
 */
function renderizar() {
    const historyList = document.getElementById('historyList');
    const chatDisplay = document.getElementById('chatDisplay');
    const previewDisplay = document.getElementById('previewDisplay');
    const chatAtual = conversas.find(c => c.id === idAtivo);

    if (!chatAtual) return;

    // --- 1. Renderizar Histórico (Barra lateral) ---
    if (historyList) {
        historyList.innerHTML = '';
        conversas.forEach(c => {
            const card = document.createElement('div');
            card.className = `history-card ${c.id === idAtivo ? 'active-chat' : ''}`;
            card.innerHTML = `
                <input type="text" value="${c.nome}" style="background:transparent; border:none; font-weight:bold; color:inherit; outline:none; width:100%;">
                <div style="font-size:10px; margin-top:5px; opacity:0.7;">${c.mensagens.length} Mensagens</div>
            `;
            card.onclick = (e) => { if(e.target.tagName !== 'INPUT') mudarConversa(c.id) };
            historyList.appendChild(card);
        });
    }

    // --- 2. Renderizar Header do Chat ---
    const titleElement = document.getElementById('currentChatTitle');
    if (titleElement) titleElement.innerText = chatAtual.nome;

    // --- 3. Renderizar Mensagens (Balões) ---
    if (chatDisplay) {
        chatDisplay.innerHTML = '';
        chatAtual.mensagens.forEach(m => {
            // Usa as classes conforme a imagem de referência: bot-msg (cinza) e user-msg (rosa)
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${m.tipo}-msg`;
            msgDiv.innerHTML = `
                ${m.texto.replace(/\n/g, '<br>')}
                <span style="display:block; font-size:9px; margin-top:5px; opacity:0.5; text-align:right;">${m.hora}</span>
            `;
            chatDisplay.appendChild(msgDiv);
        });
        // Scroll automático para a última mensagem
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }

    // --- 4. Renderizar Orçamento (Painel Direito) ---
    if (previewDisplay) {
        previewDisplay.innerHTML = '<h4 style="text-align:center; color:white; font-weight:700; margin-bottom:15px;">Prévia do Orçamento</h4>';
        chatAtual.itensOrcamento.forEach(o => {
            previewDisplay.innerHTML += `
                <div class="preview-card" style="background:#D9D9D9; border-radius:20px; padding:15px; margin-bottom:15px; color:#444;">
                    <div style="color:${o.tipo === 'green' ? '#28a745' : '#dc3545'}; font-weight:bold; margin-bottom:5px; text-transform:uppercase; font-size:12px;">
                        ${o.status}
                    </div>
                    <p style="font-size:13px; line-height:1.4;">${o.texto}</p>
                    <div style="margin-top:10px; display:flex; flex-direction:column; gap:5px;">
                        <button style="width:100%; padding:6px; border-radius:10px; border:1px solid #999; background:white; cursor:pointer; font-size:11px;">Ver Detalhes</button>
                        <button style="width:100%; padding:6px; border-radius:10px; border:1px solid #aaa; background:none; cursor:pointer; font-size:11px;">Excluir</button>
                    </div>
                    <p style="font-size:9px; margin-top:10px; text-align:center; opacity:0.5;">Código: ${o.cod || 'conv-001'}</p>
                </div>
            `;
        });
    }
}

// Inicializa a interface ao carregar a página
window.onload = renderizar;