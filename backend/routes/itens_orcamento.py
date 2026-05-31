from flask import Blueprint, request, jsonify
from banco import itens_orcamento_collection, produtos_collection, orcamentos_collection
from bson import ObjectId

itens_orcamento_bp = Blueprint("itens_orcamento", __name__)


def calcular_subtotal(quantidade, preco_unitario):
    return quantidade * preco_unitario


@itens_orcamento_bp.route("/itens-orcamento", methods=["POST"])
def criar_item_orcamento():
    data = request.json

    campos = [
        "quantidade",
        "produtoId",
        "orcamentoId"
    ]

    for campo in campos:
        if campo not in data:
            return jsonify({
                "erro": f"Campo obrigatório: {campo}"
            }), 400

    quantidade = int(data["quantidade"])

    if quantidade <= 0:
        return jsonify({
            "erro": "Quantidade deve ser maior que zero"
        }), 400

    try:
        produto = produtos_collection.find_one({
            "_id": ObjectId(data["produtoId"])
        })

        orcamento = orcamentos_collection.find_one({
            "_id": ObjectId(data["orcamentoId"])
        })

    except:
        return jsonify({
            "erro": "produtoId ou orcamentoId inválido"
        }), 400

    if not produto:
        return jsonify({
            "erro": "Produto não encontrado"
        }), 404

    if not orcamento:
        return jsonify({
            "erro": "Orçamento não encontrado"
        }), 404

    preco_unitario = float(produto["precoBase"])
    subtotal = calcular_subtotal(quantidade, preco_unitario)

    item = {
        "quantidade": quantidade,
        "precoUnitario": preco_unitario,
        "subtotal": subtotal,
        "produtoId": data["produtoId"],
        "orcamentoId": data["orcamentoId"],
        "valorFrete": data.get("valorFrete", 0),
        "tempoEntrega": data.get("tempoEntrega", 0)
    }

    result = itens_orcamento_collection.insert_one(item)

    item["_id"] = str(result.inserted_id)

    return jsonify({
        "msg": "Item do orçamento criado com sucesso",
        "id": str(result.inserted_id),
        "item": item
}), 201


@itens_orcamento_bp.route("/itens-orcamento", methods=["GET"])
def listar_itens_orcamento():
    itens = []

    for item in itens_orcamento_collection.find():
        item["_id"] = str(item["_id"])
        itens.append(item)

    return jsonify(itens)


@itens_orcamento_bp.route("/itens-orcamento/<id>", methods=["GET"])
def buscar_item_orcamento(id):
    try:
        item = itens_orcamento_collection.find_one({
            "_id": ObjectId(id)
        })
    except:
        return jsonify({
            "erro": "ID inválido"
        }), 400

    if not item:
        return jsonify({
            "erro": "Item do orçamento não encontrado"
        }), 404

    item["_id"] = str(item["_id"])

    return jsonify(item)


@itens_orcamento_bp.route("/itens-orcamento/<id>/quantidade", methods=["PUT"])
def atualizar_quantidade(id):
    data = request.json

    if "quantidade" not in data:
        return jsonify({
            "erro": "Campo obrigatório: quantidade"
        }), 400

    quantidade = int(data["quantidade"])

    if quantidade <= 0:
        return jsonify({
            "erro": "Quantidade deve ser maior que zero"
        }), 400

    try:
        item = itens_orcamento_collection.find_one({
            "_id": ObjectId(id)
        })
    except:
        return jsonify({
            "erro": "ID inválido"
        }), 400

    if not item:
        return jsonify({
            "erro": "Item do orçamento não encontrado"
        }), 404

    preco_unitario = float(item["precoUnitario"])
    subtotal = calcular_subtotal(quantidade, preco_unitario)

    itens_orcamento_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "quantidade": quantidade,
            "subtotal": subtotal
        }}
    )

    return jsonify({
        "msg": "Quantidade atualizada com sucesso",
        "subtotal": subtotal
    })


@itens_orcamento_bp.route("/itens-orcamento/<id>", methods=["DELETE"])
def deletar_item_orcamento(id):
    try:
        result = itens_orcamento_collection.delete_one({
            "_id": ObjectId(id)
        })
    except:
        return jsonify({
            "erro": "ID inválido"
        }), 400

    if result.deleted_count == 0:
        return jsonify({
            "erro": "Item do orçamento não encontrado"
        }), 404

    return jsonify({
        "msg": "Item do orçamento deletado com sucesso"
    })