from flask import Blueprint, request, jsonify
from banco import orcamentos_collection, insumos_collection
from bson import ObjectId
from datetime import datetime, timezone
import math 

orcamentos_bp = Blueprint("orcamentos", __name__)


def calcular_aproveitamento(larg_folha, alt_folha, larg_impressao, alt_impressao, margem= 1.0, sangria = 0.2):
    util_larg = larg_folha - (2 * margem)
    util_alt = alt_folha - (2 * margem)

    item_larg = larg_impressao + (2 * sangria)
    item_alt = alt_impressao + (2 * sangria)

    qtd_op1 = (util_larg // item_larg) * (util_alt // item_alt)
    qtd_op2 = (util_larg // item_alt) * (util_alt // item_larg)

    return int(max(qtd_op1, qtd_op2))

@orcamentos_bp.route("/orcamentos", methods=["POST"])
def criar_orcamentos():
    data = request.json

    if not data:
        return jsonify({
            "erro": "Dados não enviados"
        }), 400
    
    campos_obrigatorios = [
        "categoria", 
        "quantidade_convites",
        "largura_folha",
        "altura_folha",
        "largura_impressao",
        "altura_impressao"
    ]

    for campo in campos_obrigatorios: 
        if campo not in data:
            return jsonify({
                "erro": f"Campo obrigatório: {campo}"
            }), 400
        
    categoria = data["categoria"]
    quantidade_convites = data["quantidade_convites"]
    largura_folha = data["largura_folha"]
    altura_folha = data["altura_folha"]
    largura_impressao = data["largura_impressao"]
    altura_impressao = data["altura_impressao"]
    margem = data.get("margem", 1.0)
    sangria = data.get("sangria", 0.2)
    margem_lucro = data.get("margem_lucro", 1.0)

    if quantidade_convites <= 0:
        return jsonify({
            "erro": "A quantidade de convites deve ser maior que zero"
        }), 400
    
    insumo = insumos_collection.find_one({
        "categoria" : categoria
    })

    if not insumo:
        return jsonify({
            "erro": "Insumo não encontrado"
        }), 404
    

    preco_unitario = float(insumo["preco_unitario"])
    estoque_disponivel = int(insumo.get("estoque_disponivel",0))

    aproveitamento = calcular_aproveitamento(
        largura_folha,
        altura_folha,
        largura_impressao,
        altura_impressao,
        margem,
        sangria
    )

    if aproveitamento <= 0:
        return jsonify({
            "erro": "Não foi póssivel calcular o aproveitamento com essas dimensões"
        }), 400
    
    folhas_necessarias = math.ceil(quantidade_convites / aproveitamento)

    if estoque_disponivel < folhas_necessarias:
        return jsonify({
            "erro": "Estoque insuficiente para esse orçamento"
        }), 400
    
    custo_total = folhas_necessarias * preco_unitario
    valor_final = custo_total + (custo_total * margem_lucro / 100)

    orcamento = {
        "categoria": categoria,
        "quantidade_convites":quantidade_convites,
        "largura_folha": largura_folha,
        "altura_folha": altura_folha,
        "largura_impressao": largura_impressao,
        "altura_impressao": altura_impressao,
        "margem": margem,
        "sangria": sangria,
        "aproveitamento": aproveitamento,
        "folhas_necessarias": folhas_necessarias,
        "preco_unitario_folha": preco_unitario,
        "custo_total": custo_total,
        "margem_lucro": margem_lucro,
        "valor_final": valor_final,
        "data_criacao": datetime.now(timezone.utc) 
    }

    result = orcamentos_collection.insert_one(orcamento)

    return jsonify({
        "msg": "Orçaemento criado com sucesso",
        "id": str(result.inserted_id),
        "orcamento":{
            "categoria": categoria,
            "quantidade_convites": quantidade_convites,
            "aproveitamento": aproveitamento,
            "folhas_necessarias": folhas_necessarias,
            "preco_unitario_folha": preco_unitario,
            "custo_total": margem_lucro,
            "valor_final": valor_final
        }
    }), 201

@orcamentos_bp.route("/orcamentos", methods=["GET"])
def listar_orcamentos():
    orcamentos = []

    for orcamento in orcamentos_collection.find():
        orcamento["_id"] = str(orcamento["_id"])

        if "data_criacao" in orcamento:
            orcamento["data_criacao"] = orcamento["data_criacao"].isoformat()

            orcamentos.append(orcamento)

    return jsonify(orcamentos)
    
@orcamentos_bp.route("/orcamentos/<id>", methods=["GET"])
def buscar_orcamento(id):
    try:
        orcamento = orcamentos_collection.find_one({
            "_id": ObjectId(id)
        })
    except:
        return jsonify({
            "erro": "ID inválido"
        }), 400
    
    if not orcamento:
        return jsonify({
            "erro": "Orçamento não encontrado"
        }), 404
    
    orcamento["_id"] = str(orcamento["_id"])

    if "data_criacao" in orcamento:
        orcamento["data_criacao"] = orcamento["data_criacao"].isoformat()

    return jsonify(orcamento)

@orcamentos_bp.route("/orcamento/<id>", methods=["DELETE"])
def deletar_orcamento(id):
    try:
        result = orcamentos_collection.delete_one({
            "_id": ObjectId(id)
        })
    except:
        return jsonify({
            "erro": "ID inválido"
        }), 400
    
    if result.deleted_count == 0:
        return jsonify({
            "erro": "Orçamento não econtrado"
        }), 404
    
    return jsonify({
        "msg": "Orçamento deletado com sucesso"
    })