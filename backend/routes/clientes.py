from flask import Blueprint, request, jsonify
from backend.banco import clientes_collection #caminho para pasta 
from bson import ObjectId
from datetime import datetime

clientes_bp = Blueprint("clientes", __name__)

@clientes_bp.route("/clientes", methods=["POST"])
def criar_cliente():

    data = request.json

    campos = [
        "nome",
        "telefone"
    ]

    for campo in campos:
        if campo not in data:
            return jsonify({
                "erro": f"Campo obrigatório: {campo}"
            }), 400

    cliente = {
        "nome": data["nome"],
        "email": data.get("email", ""),
        "telefone": data["telefone"],
        "endereco": data.get("endereco", ""),
        "tipoCliente": data.get("tipoCliente", "comum"),
        "dataCadastro": datetime.now()
    }

    result = clientes_collection.insert_one(cliente)

    return jsonify({
        "msg": "Cliente cadastrado com sucesso",
        "id": str(result.inserted_id)
    }), 201

@clientes_bp.route("/clientes", methods=["GET"])
def listar_clientes():

    clientes = []

    for cliente in clientes_collection.find():

        cliente["_id"] = str(cliente["_id"])

        clientes.append(cliente)

    return jsonify(clientes)

@clientes_bp.route("/clientes/telefone/<telefone>", methods=["GET"])
def buscar_por_telefone(telefone):

    cliente = clientes_collection.find_one({
        "telefone": telefone
    })

    if not cliente:
        return jsonify({
            "erro": "Cliente não encontrado"
        }), 404

    cliente["_id"] = str(cliente["_id"])

    return jsonify(cliente)

@clientes_bp.route("/clientes/<id>", methods=["PUT"])
def atualizar_cliente(id):

    data = request.json

    try:

        result = clientes_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )

    except:
        return jsonify({
            "erro": "ID inválido"
        }), 400

    if result.matched_count == 0:
        return jsonify({
            "erro": "Cliente não encontrado"
        }), 404

    return jsonify({
        "msg": "Cliente atualizado com sucesso"
    })

@clientes_bp.route("/clientes/<id>/desativar", methods=["PUT"])
def desativar_cliente(id):

    try:

        result = clientes_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"ativo": False}}
        )

    except:
        return jsonify({
            "erro": "ID inválido"
        }), 400

    if result.matched_count == 0:
        return jsonify({
            "erro": "Cliente não encontrado"
        }), 404

    return jsonify({
        "msg": "Cliente desativado"
    })