from flask import Blueprint, request, jsonify
from banco import tipos_produto_collection
from bson import ObjectId

tipos_produto_bp = Blueprint("tipos_produto", __name__)


def calcular_area(largura, comprimento):
    return largura * comprimento


def calcular_volume(largura, comprimento, gramadura):
    return largura * comprimento * gramadura


def validar_dimensoes(gramadura, largura, comprimento):
    return gramadura > 0 and largura > 0 and comprimento > 0


@tipos_produto_bp.route("/tipos-produto", methods=["POST"])
def criar_tipo_produto():
    data = request.json

    campos = ["gramadura", "largura", "comprimento"]

    for campo in campos:
        if campo not in data:
            return jsonify({
                "erro": f"Campo obrigatório: {campo}"
            }), 400

    gramadura = float(data["gramadura"])
    largura = float(data["largura"])
    comprimento = float(data["comprimento"])

    if not validar_dimensoes(gramadura, largura, comprimento):
        return jsonify({
            "erro": "Gramadura, largura e comprimento devem ser maiores que zero"
        }), 400

    area = calcular_area(largura, comprimento)
    volume = calcular_volume(largura, comprimento, gramadura)

    tipo_produto = {
        "gramadura": gramadura,
        "largura": largura,
        "comprimento": comprimento,
        "area": area,
        "volume": volume
    }

    result = tipos_produto_collection.insert_one(tipo_produto)

    return jsonify({
        "msg": "Tipo de produto criado com sucesso",
        "id": str(result.inserted_id),
        "tipoProduto": {
            "gramadura": gramadura,
            "largura": largura,
            "comprimento": comprimento,
            "area": area,
            "volume": volume
        }
    }), 201


@tipos_produto_bp.route("/tipos-produto", methods=["GET"])
def listar_tipos_produto():
    tipos = []

    for tipo in tipos_produto_collection.find():
        tipo["_id"] = str(tipo["_id"])
        tipos.append(tipo)

    return jsonify(tipos)


@tipos_produto_bp.route("/tipos-produto/<id>", methods=["GET"])
def buscar_tipo_produto(id):
    try:
        tipo = tipos_produto_collection.find_one({
            "_id": ObjectId(id)
        })
    except:
        return jsonify({
            "erro": "ID inválido"
        }), 400

    if not tipo:
        return jsonify({
            "erro": "Tipo de produto não encontrado"
        }), 404

    tipo["_id"] = str(tipo["_id"])

    return jsonify(tipo)


@tipos_produto_bp.route("/tipos-produto/<id>", methods=["PUT"])
def atualizar_tipo_produto(id):
    data = request.json

    try:
        tipo_existente = tipos_produto_collection.find_one({
            "_id": ObjectId(id)
        })
    except:
        return jsonify({
            "erro": "ID inválido"
        }), 400

    if not tipo_existente:
        return jsonify({
            "erro": "Tipo de produto não encontrado"
        }), 404

    gramadura = float(data.get("gramadura", tipo_existente["gramadura"]))
    largura = float(data.get("largura", tipo_existente["largura"]))
    comprimento = float(data.get("comprimento", tipo_existente["comprimento"]))

    if not validar_dimensoes(gramadura, largura, comprimento):
        return jsonify({
            "erro": "Gramadura, largura e comprimento devem ser maiores que zero"
        }), 400

    area = calcular_area(largura, comprimento)
    volume = calcular_volume(largura, comprimento, gramadura)

    tipos_produto_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "gramadura": gramadura,
            "largura": largura,
            "comprimento": comprimento,
            "area": area,
            "volume": volume
        }}
    )

    return jsonify({
        "msg": "Tipo de produto atualizado com sucesso"
    })


@tipos_produto_bp.route("/tipos-produto/<id>", methods=["DELETE"])
def deletar_tipo_produto(id):
    try:
        result = tipos_produto_collection.delete_one({
            "_id": ObjectId(id)
        })
    except:
        return jsonify({
            "erro": "ID inválido"
        }), 400

    if result.deleted_count == 0:
        return jsonify({
            "erro": "Tipo de produto não encontrado"
        }), 404

    return jsonify({
        "msg": "Tipo de produto deletado com sucesso"
    })