from flask import Blueprint, request, jsonify
from banco import modelos_personalizados_collection
from bson import ObjectId
from datetime import datetime

modelos_personalizados_bp = Blueprint("modelos_personalizados", __name__)


def calcular_valor_personalizacao(valor_base, acrescimo):
    return float(valor_base) + float(acrescimo)


def gerar_descricao_modelo(nome_modelo, tipo_personalizacao):
    return f"Modelo {nome_modelo} com personalização do tipo {tipo_personalizacao}"


@modelos_personalizados_bp.route("/modelos-personalizados", methods=["POST"])
def criar_modelo_personalizado():
    data = request.json

    campos = [
        "nomeModelo",
        "tipoPersonalizacao",
        "valorBase",
        "acrescimo"
    ]

    for campo in campos:
        if campo not in data:
            return jsonify({
                "erro": f"Campo obrigatório: {campo}"
            }), 400

    valor_total = calcular_valor_personalizacao(
        data["valorBase"],
        data["acrescimo"]
    )

    descricao = data.get(
        "descricao",
        gerar_descricao_modelo(data["nomeModelo"], data["tipoPersonalizacao"])
    )

    modelo = {
        "nomeModelo": data["nomeModelo"],
        "descricao": descricao,
        "tipoPersonalizacao": data["tipoPersonalizacao"],
        "valorTotal": valor_total,
        "dataCriacao": datetime.now()
    }

    result = modelos_personalizados_collection.insert_one(modelo)

    modelo["_id"] = str(result.inserted_id)

    return jsonify({
        "msg": "Modelo personalizado criado com sucesso",
        "id": str(result.inserted_id),
        "modelo": modelo
    }), 201


@modelos_personalizados_bp.route("/modelos-personalizados", methods=["GET"])
def listar_modelos_personalizados():
    modelos = []

    for modelo in modelos_personalizados_collection.find():
        modelo["_id"] = str(modelo["_id"])

        if "dataCriacao" in modelo:
            modelo["dataCriacao"] = modelo["dataCriacao"].isoformat()

        modelos.append(modelo)

    return jsonify(modelos)


@modelos_personalizados_bp.route("/modelos-personalizados/<id>", methods=["GET"])
def buscar_modelo_personalizado(id):
    try:
        modelo = modelos_personalizados_collection.find_one({
            "_id": ObjectId(id)
        })
    except:
        return jsonify({
            "erro": "ID inválido"
        }), 400

    if not modelo:
        return jsonify({
            "erro": "Modelo personalizado não encontrado"
        }), 404

    modelo["_id"] = str(modelo["_id"])

    if "dataCriacao" in modelo:
        modelo["dataCriacao"] = modelo["dataCriacao"].isoformat()

    return jsonify(modelo)


@modelos_personalizados_bp.route("/modelos-personalizados/<id>", methods=["PUT"])
def atualizar_modelo_personalizado(id):
    data = request.json

    try:
        modelo_existente = modelos_personalizados_collection.find_one({
            "_id": ObjectId(id)
        })
    except:
        return jsonify({
            "erro": "ID inválido"
        }), 400

    if not modelo_existente:
        return jsonify({
            "erro": "Modelo personalizado não encontrado"
        }), 404

    atualizacao = {}

    if "nomeModelo" in data:
        atualizacao["nomeModelo"] = data["nomeModelo"]

    if "descricao" in data:
        atualizacao["descricao"] = data["descricao"]

    if "tipoPersonalizacao" in data:
        atualizacao["tipoPersonalizacao"] = data["tipoPersonalizacao"]

    if "valorBase" in data and "acrescimo" in data:
        atualizacao["valorTotal"] = calcular_valor_personalizacao(
            data["valorBase"],
            data["acrescimo"]
        )

    if not atualizacao:
        return jsonify({
            "erro": "Nenhum campo enviado para atualização"
        }), 400

    modelos_personalizados_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": atualizacao}
    )

    return jsonify({
        "msg": "Modelo personalizado atualizado com sucesso"
    })


@modelos_personalizados_bp.route("/modelos-personalizados/<id>", methods=["DELETE"])
def deletar_modelo_personalizado(id):
    try:
        result = modelos_personalizados_collection.delete_one({
            "_id": ObjectId(id)
        })
    except:
        return jsonify({
            "erro": "ID inválido"
        }), 400

    if result.deleted_count == 0:
        return jsonify({
            "erro": "Modelo personalizado não encontrado"
        }), 404

    return jsonify({
        "msg": "Modelo personalizado deletado com sucesso"
    })