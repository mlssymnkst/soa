'use strict';

/* Estado Geral do Chatbot */
const state = {
    conversations: [],      // lista de conversas
    activeConvId: null,     // id da conversa selecionada
    messages: [],           // quantidade de mensagens da conversa ativa
    quoteItems: [],         // itens do orçamento da conversa ativa
    menuOpen: false,        // menu lateral sempre começa fechado
    convCounter: 0,         // contador de conversas
    quoteCounter: 0,        // contador de itens no orçamento
};

/* Data e Hora */
function now() {
    return new Date().toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'});
}

function dateStr(timestamp) {
    const diff = Date.now() - timestamp;
    if (diff < 60_000)
        return 'Agora';
    
    if (diff < 3_600_000)
        return Math.floor (diff / 60_000) + 'min atrás';
    
    return new Date(timestamp).toLocaleDateString('pt-BR', {day: '2-digit', month: '2-digit'});  
}

/* --------------------------------------------------------------------
MENU LATERAL (Histórico de Conversas)
 -------------------------------------------------------------------- */

function toggleMenu() {
    state.menuOpen = !state.menuOpen;
    document.getElementById('menuSidebar').classList.toggle ('open' , state.menuOpen);
    document.getElementById('overlay').classList.toggle('visible', state.menuOpen);
    document.getElementById('menuToggleBtn').classList.toggle('active', state.menuOpen);
}