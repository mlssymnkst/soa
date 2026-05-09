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

# ─────────────────────────────────────────────
# ROTA: Iniciar sessão
# ─────────────────────────────────────────────
@bot_bp.route("/bot/iniciar", methods=["POST"])
def inciar_sessao():
    sid = str(uuid.uuid4())
    _sessoes[sid] = {
        "etapa": "pedir_produto",
        "produto_atual": {},
        "itens": [],    # produtos que foram confirmados
        "endereço": None,
        "frete": None,
        "valor_total": 0,
    }
    return jsonify({"session_id": sid, # mudar a função no js **_proxima_mensagem(sid)})
                    