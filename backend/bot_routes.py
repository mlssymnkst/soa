from flask import Blueprint, request, jsonify
from bson import ObjectId
import uuid
import math
from datetime import datetime
from banco import insumos_collection, orcamentos_collection, produtos_collection

bot_bp = Blueprint("bot", __name__)

# ─────────────────────────────────────────────
# Sessões em memória (uma por aba/usuário)
# ─────────────────────────────────────────────
_sessoes: dict = {}

# ══════════════════════════════════════════════
# UTILITÁRIOS  (definidos primeiro para evitar aviso do Pylance)
# ══════════════════════════════════════════════
 
def is_sim(t: str) -> bool:
    return t.strip().lower() in {"sim", "s", "yes", "y", "1"}
 
def is_nao(t: str) -> bool:
    return t.strip().lower() in {"não", "nao", "n", "no", "0"}
 
def casar(user_input: str, opcoes: list):
    """Casa input com opção da lista por índice, nome exato ou parcial."""
    cleaned = user_input.strip()
    if cleaned.isdigit():
        idx = int(cleaned) - 1
        if 0 <= idx < len(opcoes):
            return opcoes[idx]
    for opt in opcoes:
        if opt.lower() == cleaned.lower():
            return opt
    for opt in opcoes:
        if cleaned.lower() in opt.lower():
            return opt
    return None

# ══════════════════════════════════════════════
# QUERIES AO MONGODB
# ══════════════════════════════════════════════

""" PLACEHOLDERS """
def papeis_placeholder():
    return [
        {"modelo": "Couchê 115g", "aproveitamento": 4, "preco_venda": 0.35, "peso_por_folha_g": 18.5},
        {"modelo": "Couchê 250g", "aproveitamento": 2, "preco_venda": 0.75, "peso_por_folha_g": 40.0},
        {"modelo": "Couchê 300g", "aproveitamento": 2, "preco_venda": 0.90, "peso_por_folha_g": 48.0},
        {"modelo": "Offset 75g",  "aproveitamento": 4, "preco_venda": 0.20, "peso_por_folha_g": 12.0},
    ]
 
def fitas_placeholder():
    return [
        {"modelo": "Fita Cetim 1cm",   "preco_por_cm": 0.012},
        {"modelo": "Fita Cetim 2,5cm", "preco_por_cm": 0.025},
        {"modelo": "Fita Veludo 1cm",  "preco_por_cm": 0.020},
        {"modelo": "Fita Organza 2cm", "preco_por_cm": 0.018},
    ]

def adicionais_placeholder():
    return [
        {"modelo": "Lenço Unitário",   "preco_por_unid": 0.10},
        {"modelo": "Arroz 15g", "preco_por_unid": 0.015},
        {"modelo": "Embalagem plástico lenço",  "preco_por_unid": 0.20},
        {"modelo": "Embalagem plástico arroz", "preco_por_unid": 0.18},
    ]
 
 # *********************************
 # FUNÇÕES
 
def listar_categorias_insumos() -> list:
    try:
        cats = insumos_collection.distinct("categoria")
        return [c for c in cats if c]
    except Exception:
        return ["Convite", "Lenço", "Cardápio", "Tag", "Envelope"]
 
def listar_modelos(produto: str) -> list:
    try:
        return list(insumos_collection.find(
            {"categoria": produto, "modelo": {"$exists": True, "$ne": ""}},
            {"_id": 1, "modelo": 1, "papel": 1, "envelope": 1, "tamanho": 1,
             "aproveitamento": 1, "preco_venda": 1, "peso_por_folha_g": 1}
        ))
    except Exception:
        return []
 
def listar_envelopes() -> list:
    try:
        docs = insumos_collection.distinct("envelope")
        return [e for e in docs if e] or ["Envelope Kraft", "Envelope Branco", "Envelope Colorido", "Envelope Translúcido"]
    except Exception:
        return ["Envelope Kraft", "Envelope Branco", "Envelope Colorido", "Envelope Translúcido"]
 
def listar_papeis() -> list:
    try:
        docs = list(insumos_collection.find(
            {"$or": [{"categoria": "papel"}, {"tipo": "papel"}]},
            {"_id": 1, "modelo": 1, "aproveitamento": 1, "preco_venda": 1, "peso_por_folha_g": 1}
        ))
        return docs or papeis_placeholder()
    except Exception:
        return papeis_placeholder()
 
def listar_fitas() -> list:
    try:
        docs = list(insumos_collection.find(
            {"$or": [{"categoria": "fita"}, {"tipo": "fita"}]},
            {"_id": 1, "modelo": 1, "preco_por_cm": 1}
        ))
        return docs or fitas_placeholder()
    except Exception:
        return fitas_placeholder()
    
def listar_adicionais() -> list:
    try:
        docs = insumos_collection.distinct("adicionais")
        return [e for e in docs if e] or adicionais_placeholder()
    except Exception:
        return adicionais_placeholder()

# ══════════════════════════════════════════════
# FRETE
# ══════════════════════════════════════════════
 
FRETE_GRATIS = 350.0
 
def calcular_frete(valor_total: float, peso_gramas: float, endereco: str) -> dict:
    if valor_total >= FRETE_GRATIS:
        return {"valor": 0.0, "prazo_dias": 7, "transportadora": "Frete grátis"}
    # TODO: Integrar com API de frete real (ex: Melhor Envio, Correios)
    peso_kg = peso_gramas / 1000
    return {
        "valor":          round(15.0 + (peso_kg * 3.5), 2),
        "prazo_dias":     5,
        "transportadora": "A definir",
        "obs":            "Valor simulado — integração com API de frete pendente",
    }
# ══════════════════════════════════════════════
# HELPERS DE FLUXO
# ══════════════════════════════════════════════
 
def proxima_mensagem(sid: str) -> dict:
    s      = _sessoes[sid]
    etapa  = s["etapa"]
    produto = s["produto_atual"].get("produto", "")
 
    prompts = {
        "pedir_produto":    {"mensagem": "Qual o produto desejado?",
                             "opcoes":   listar_categorias_insumos()},

        "pedir_quantidade": {"mensagem": "Qual a quantidade de unidades?", "opcoes": []},

        "tem_modelo":       {"mensagem": f"O produto *{produto}* tem um modelo pronto?",
                             "opcoes":   ["Sim", "Não"]},

        "pedir_modelo":     {"mensagem": "Qual modelo?",
                             "opcoes":   [m["modelo"] for m in listar_modelos(produto)]},

        "pedir_envelope":  {"mensagem": "Qual envelope será utilizado?",
                             "opcoes":   listar_envelopes()},

        "pedir_tamanho":    {"mensagem": "Qual o tamanho das impressões? (ex: 10x15, 148x210)",
                             "opcoes":   []},

        "pedir_papel":      {"mensagem": "Qual papel será utilizado?",
                             "opcoes":   [p["modelo"] for p in listar_papeis()]},

        "pedir_fita":       {"mensagem": "Será utilizada alguma fita?", "opcoes": ["Sim", "Não"]},
        "pedir_qual_fita":  {"mensagem": "Qual fita?",
                             "opcoes":   [f["modelo"] for f in listar_fitas()]},

        "pedir_cm_fita":    {"mensagem": "Quantos cm de fita por unidade?", "opcoes": []},

        "pedir_adicional":       {"mensagem": "Será adicionado algum adicional? (Embalagem, arroz, lenço)",
                                  "opcoes":   ["Sim", "Não"]},
        "pedir_qual_adicional":  {"mensagem": "Qual adicional?",
                                  "opcoes":   [a["modelo"] for a in listar_adicionais()]},
        "pedir_endereco":   {"mensagem": "Qual o endereço de entrega? (rua, número, cidade e CEP)",
                             "opcoes":   []},

#**********************************************
# COLOQUEI PARA PEDIR O ENDEREÇO, MAS TERIA QUE ADAPTAR AS FUNÇÕES PARA PEDIR O ENDEREÇO APENAS NO FINAL ?
# *********************************************

    }
    return prompts.get(etapa, {"mensagem": "...", "opcoes": []})
 
def confirmar_produto(sid: str) -> dict:
    s = _sessoes[sid]
    p = s["produto_atual"]
    s["itens"].append(dict(p))  # copia para não referenciar o mesmo dict
 
    custo  = round(p.get("custo_papel", 0) + p.get("custo_fita", 0), 2)
    resumo = (
        f"✅ *{p['produto']}* adicionado!\n"
        f"• Quantidade: {p['quantidade']} unidades\n"
        f"• Papel: {p.get('papel','—')} ({p.get('qtde_folhas','—')} folhas)\n"
    )
    if p.get("fita"):
        resumo += f"• Fita: {p['fita']} — {p.get('cm_fita_por_unidade', 0)}cm/un\n"
    resumo += f"• Custo parcial: R$ {custo:.2f}\n\nQuer adicionar mais algum produto ao orçamento?"

    s["etapa"] = "perguntar_mais"
    return {
        "mensagem": resumo,
        "opcoes":   ["Sim", "Não"],
        "acao":     "item_adicionado",
        "item": {
            "titulo":     p["produto"],
            "papel":      p.get("papel", "—"),
            "envelope":  p.get("envelope", "—"),
            "quantidade": p["quantidade"],
            "fita":       p.get("fita", "Nenhuma"),
            "custo":      custo,
        },
    }

def resumo_orcamento(sid: str) -> dict:
    s     = _sessoes[sid]
    linhas = ["📋 *Resumo do Orçamento*\n"]
    total  = 0
    for i, p in enumerate(s["itens"], 1):
        sub    = p.get("custo_papel", 0) + p.get("custo_fita", 0)
        total += sub
        linhas.append(
            f"{i}. {p['produto']} — {p['quantidade']} un | {p.get('papel','—')} | "
            f"Fita: {p.get('fita','Nenhuma')} | R$ {sub:.2f}"
        )
    linhas.append(f"\n💰 Subtotal: R$ {total:.2f}\n\nEsse pedido foi finalizado?")
    return {"mensagem": "\n".join(linhas), "opcoes": ["Sim", "Não"]}

# ══════════════════════════════════════════════
# HANDLERS DE CADA ETAPA
# ══════════════════════════════════════════════
 
def h_produto(sid: str, txt: str) -> dict:
    s        =_sessoes[sid]
    produtos = listar_categorias_insumos()
    match    = casar(txt, produtos)
    if not match:
        return {"mensagem": "Produto não encontrado. Escolha um da lista:", "opcoes": produtos}
    s["produto_atual"] = {"produto": match}
    s["etapa"]         = "pedir_quantidade"
    return proxima_mensagem(sid)
 
 
def h_quantidade(sid: str, txt: str) -> dict:
    s =_sessoes[sid]
    if not txt.isdigit() or int(txt) <= 0:
        return {"mensagem": "Informe uma quantidade válida (número inteiro positivo).", "opcoes": []}
    s["produto_atual"]["quantidade"] = int(txt)
    s["etapa"] = "tem_modelo"
    return proxima_mensagem(sid)
 
 
def h_tem_modelo(sid: str, txt: str) -> dict:
    s       =_sessoes[sid]
    produto = s["produto_atual"]["produto"]
    if is_sim(txt):
        modelos = listar_modelos(produto)
        if not modelos:
            s["etapa"] = "pedir_envelope"
            return {"mensagem": f"Não há modelos prontos para '{produto}'. Vamos configurar manualmente.\n\nQual envelope será utilizado?",
                    "opcoes": listar_envelopes()}
        s["etapa"] = "pedir_modelo"
        return proxima_mensagem(sid)
    elif is_nao(txt):
        s["etapa"] = "pedir_envelope"
        return proxima_mensagem(sid)
    return {"mensagem": "Responda Sim ou Não.", "opcoes": ["Sim", "Não"]}
 
 
def h_modelo(sid: str, txt: str) -> dict:
    s       =_sessoes[sid]
    produto = s["produto_atual"]["produto"]
    modelos = listar_modelos(produto)
    nomes   = [m["modelo"] for m in modelos]
    nome    = casar(txt, nomes)
    if not nome:
        return {"mensagem": "Modelo não encontrado. Escolha um da lista:", "opcoes": nomes}
    modelo = next(m for m in modelos if m["modelo"] == nome)
    qtde   = s["produto_atual"]["quantidade"]
    ap     = modelo.get("aproveitamento", 1)
    folhas = math.ceil(qtde / ap)
   
    s["produto_atual"].update({
        "modelo":            nome,
        "envelope":         modelo.get("envelope", "—"),
        "tamanho_impressao": modelo.get("tamanho", "—"),
        "papel":             modelo.get("papel", "—"),
        "aproveitamento":    ap,
        "qtde_folhas":       folhas,
        "custo_papel":       round(folhas * modelo.get("preco_venda", 0), 2),
        "peso_g":            round(folhas * modelo.get("peso_por_folha_g", 0), 2),
        "insumo_id":         str(modelo.get("_id", "")),
    })
    s["etapa"] = "pedir_fita"
    return {
        "mensagem": (
            f"✅ Modelo *{nome}* selecionado!\n"
            f"📄 Papel: {modelo.get('papel','—')} | Aproveitamento: {ap}/folha | Folhas: {folhas}\n\n"
            "Será utilizada alguma fita?"
        ),
        "opcoes": ["Sim", "Não"],
    }
 
def h_envelope (sid: str, txt: str) -> dict:
    s         = _sessoes[sid]
    envelopes = listar_envelopes()
    match     = casar(txt, envelopes)
    if not match:
        return {"mensagem": "Envelope não encontrado. Escolha um da lista:", "opcoes": envelopes}
    s["produto_atual"]["envelope"] = match
    s["etapa"] = "pedir_tamanho"
    return proxima_mensagem(sid)
 
 
def h_tamanho(sid: str, txt: str) -> dict:
    s =_sessoes[sid]
    if len(txt) < 3:
        return {"mensagem": "Informe o tamanho das impressões (ex: 10x15, 148x210).", "opcoes": []}
    s["produto_atual"]["tamanho_impressao"] = txt
    s["etapa"] = "pedir_papel"
    return proxima_mensagem(sid)
 
 
def h_papel(sid: str, txt: str) -> dict:
    s      =_sessoes[sid]
    papeis = listar_papeis()
    nomes  = [p["modelo"] for p in papeis]
    nome   = casar(txt, nomes)
    if not nome:
        return {"mensagem": "Papel não encontrado. Escolha um da lista:", "opcoes": nomes}
    papel  = next(p for p in papeis if p["modelo"] == nome)
    qtde   = s["produto_atual"]["quantidade"]
    ap     = papel.get("aproveitamento", 2)
    folhas = math.ceil(qtde / ap)
    
    s["produto_atual"].update({
        "papel":          nome,
        "aproveitamento": ap,
        "qtde_folhas":    folhas,
        "custo_papel":    round(folhas * papel.get("preco_venda", 0), 2),
        "peso_g":         round(folhas * papel.get("peso_por_folha_g", 0), 2),
        "insumo_id":      str(papel.get("_id", "")),
    })
    s["etapa"] = "pedir_fita"
    return {
        "mensagem": (
            f"📄 Papel *{nome}* selecionado!\n"
            f"Aproveitamento: {ap}/folha | Folhas: {folhas}\n\n"
            "Será utilizada alguma fita?"
        ),
        "opcoes": ["Sim", "Não"],
    }
 
def h_fita(sid: str, txt: str) -> dict:
    s =_sessoes[sid]
    if is_sim(txt):
        s["etapa"] = "pedir_qual_fita"
        return proxima_mensagem(sid)
    elif is_nao(txt):
        s["produto_atual"]["fita"]       = None
        s["produto_atual"]["custo_fita"] = 0.0
        return confirmar_produto(sid)
    return {"mensagem": "Responda Sim ou Não.", "opcoes": ["Sim", "Não"]}
 
 
def h_qual_fita(sid: str, txt: str) -> dict:
    s     =_sessoes[sid]
    fitas = listar_fitas()
    nomes = [f["modelo"] for f in fitas]
    nome  = casar(txt, nomes)
    if not nome:
        return {"mensagem": "Fita não encontrada. Escolha uma da lista:", "opcoes": nomes}
    fita_doc = next(f for f in fitas if f["modelo"] == nome)
    s["produto_atual"]["fita"]         = nome
    s["produto_atual"]["preco_por_cm"] = fita_doc.get("preco_por_cm", 0)
    s["produto_atual"]["fita_id"]      = str(fita_doc.get("_id", ""))
    s["etapa"] = "pedir_cm_fita"
    return proxima_mensagem(sid)
 
 
def h_cm_fita(sid: str, txt: str) -> dict:
    s =_sessoes[sid]
    try:
        cm = float(txt.replace(",", "."))
        if cm <= 0:
            raise ValueError
    except ValueError:
        return {"mensagem": "Informe uma quantidade válida em cm (ex: 30 ou 12.5).", "opcoes": []}
    qtde         = s["produto_atual"]["quantidade"]
    preco_por_cm = s["produto_atual"].get("preco_por_cm", 0)
    s["produto_atual"]["cm_fita_por_unidade"] = cm
    s["produto_atual"]["custo_fita"]          = round(cm * qtde * preco_por_cm, 2)
    return confirmar_produto(sid)
 
 
def h_mais_produto(sid: str, txt: str) -> dict:
    s =_sessoes[sid]
    if is_sim(txt):
        s["produto_atual"] = {}
        s["etapa"]         = "pedir_produto"
        return {"mensagem": "Ótimo! Qual o próximo produto?", "opcoes": listar_categorias_insumos()}
    elif is_nao(txt):
        s["etapa"] = "pedir_finalizacao"
        return resumo_orcamento(sid)
    return {"mensagem": "Responda Sim ou Não.", "opcoes": ["Sim", "Não"]}
 
def h_devolver(sid: str, txt: str) -> dict:
    # TODO: estorno de reserva de insumos quando implementar estoque reservado
    _sessoes.pop(sid, None)
    return {
        "mensagem": (
            "❌ Pedido não finalizado.\n"
            "Os insumos foram devolvidos ao estoque e o orçamento foi cancelado.\n"
            "Clique em *Nova Conversa* para recomeçar."
        ),
        "opcoes": [],
        "acao":   "encerrado",
    }

def h_finalizacao(sid: str, txt: str) -> dict:
    s =_sessoes[sid]
    if is_sim(txt):
        s["etapa"] = "pedir_endereco"
        return proxima_mensagem(sid)
    elif is_nao(txt):
        s["etapa"] = "devolver_insumos"
        return h_devolver(sid, txt)
    return {"mensagem": "Responda Sim ou Não.", "opcoes": ["Sim", "Não"]}
 
# *****************************************
# PRECISA REVISAR O HANDLER DA ETAPA DO FRETE
# DEF API - ENDEREÇO, PESO DA ENCOMENDA ETC 
# *****************************************
def h_endereco(sid: str, txt: str) -> dict:
    s = _sessoes[sid]
    if len(txt) < 5:
        return {"mensagem": "Informe um endereço de entrega válido (rua, número, cidade e CEP).", "opcoes": []}
    s["endereco"] = txt
    subtotal   = sum(i.get("custo_papel", 0) + i.get("custo_fita", 0) for i in s["itens"])
    peso_total = sum(i.get("peso_g", 0) for i in s["itens"])
    frete      = calcular_frete(subtotal, peso_total, txt)
    valor_total = round(subtotal + frete["valor"], 2)
    s["frete"]       = frete
    s["valor_total"] = valor_total
    doc = {
        "session_id":  sid,
        "itens":       s["itens"],
        "endereco":    txt,
        "frete":       frete,
        "valor_total": valor_total,
        "criado_em":   datetime.utcnow().isoformat(),
        "status":      "finalizado",
    }
    result       = orcamentos_collection.insert_one(doc)
    orcamento_id = str(result.inserted_id)
    itens_painel = [
        {
            "titulo":     item["produto"],
            "papel":      item.get("papel", "—"),
            "envelope":   item.get("envelope", "—"),
            "quantidade": item["quantidade"],
            "fita":       item.get("fita", "Nenhuma"),
            "custo":      round(item.get("custo_papel", 0) + item.get("custo_fita", 0), 2),
        }
        for item in s["itens"]
    ]
    return {
        "mensagem": (
            f"🚚 *Frete*: R$ {frete['valor']:.2f} | Prazo: {frete['prazo_dias']} dias úteis\n"
            f"💰 *Total com frete*: R$ {valor_total:.2f}\n\n"
            f"✅ Orçamento #{orcamento_id[:8].upper()} gerado e salvo com sucesso!"
        ),
        "opcoes":       [],
        "acao":         "orcamento_gerado",
        "orcamento_id": orcamento_id,
        "itens_painel": itens_painel,
        "valor_total":  valor_total,
        "frete":        frete,
    }
# ══════════════════════════════════════════════
# MOTOR DO FLUXO
# ══════════════════════════════════════════════
 
DESPACHO = {
    "pedir_produto":     h_produto,
    "pedir_quantidade":  h_quantidade,
    "tem_modelo":        h_tem_modelo,
    "pedir_modelo":      h_modelo,
    "pedir_envelope":    h_envelope,
    "pedir_tamanho":     h_tamanho,
    "pedir_papel":       h_papel,
    "pedir_fita":        h_fita,
    "pedir_qual_fita":   h_qual_fita,
    "pedir_cm_fita":     h_cm_fita,
    "perguntar_mais":    h_mais_produto,
    "pedir_finalizacao": h_finalizacao,
    "pedir_endereco":    h_endereco,
    "devolver_insumos":  h_devolver,
}
 
def processar(sid: str, txt: str) -> dict:
    etapa = _sessoes[sid]["etapa"]
    fn    = DESPACHO.get(etapa)
    if not fn:
        return {"mensagem": "Etapa desconhecida. Reinicie a conversa.", "opcoes": []}
    return fn(sid, txt)

# ─────────────────────────────────────────────
# ROTA: Iniciar sessão
# ─────────────────────────────────────────────
@bot_bp.route("/bot/iniciar", methods=["POST"])
def iniciar_sessao():   
    sid = str(uuid.uuid4())
    _sessoes[sid] = {
        "etapa":         "pedir_produto",
        "produto_atual": {},
        "itens":         [],
        "endereco":      None,
        "frete":         None,
        "valor_total":   0,
    }
    return jsonify({"session_id": sid, **proxima_mensagem(sid)})
 
 
# ══════════════════════════════════════════════
# ROTA: Enviar resposta do usuário
# ══════════════════════════════════════════════
@bot_bp.route("/bot/mensagem", methods=["POST"])
def mensagem():
    data = request.json or {}
    sid  = data.get("session_id")
    txt  = (data.get("mensagem") or "").strip()
 
    if sid not in _sessoes:
        return jsonify({"erro": "Sessão não encontrada. Inicie uma nova conversa."}), 404
 
    return jsonify(processar(sid, txt))

# ══════════════════════════════════════════════
# ROTA: Encerrar sessão (cancelamento)
# ══════════════════════════════════════════════
@bot_bp.route("/bot/encerrar", methods=["POST"])
def encerrar():
    data = request.json or {}
    sid  = data.get("session_id")
    _sessoes.pop(sid, None)
    return jsonify({"mensagem": "Sessão encerrada."})