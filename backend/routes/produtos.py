from flask import Blueprint, request, jsonify
from backend.banco import produtos_collection, tipos_produto_collection #caminho para pasta
from bson import ObjectId

produtos_bp = Blueprint("produtos", __name__)


@produtos_bp.route("/produtos", methods=["POST"])
def criar_produto():

    data = request.json

    campos = [
        "nome",
        "descricao",
        "precoBase",
        "tipoProdutoId"
    ]

    for campo in campos:

        if campo not in data:

            return jsonify({
                "erro": f"Campo obrigatório: {campo}"
            }), 400

    # VALIDA O TIPO DE PRODUTO

    try:

        tipo_produto = tipos_produto_collection.find_one({
            "_id": ObjectId(data["tipoProdutoId"])
        })

    except:

        return jsonify({
            "erro": "tipoProdutoId inválido"
        }), 400

    if not tipo_produto:

        return jsonify({
            "erro": "TipoProduto não encontrado"
        }), 404

    produto = {

        "nome": data["nome"],
        "descricao": data["descricao"],
        "precoBase": float(data["precoBase"]),
        "ativo": True,
        "tipoProdutoId": data["tipoProdutoId"]

    }

    result = produtos_collection.insert_one(produto)

    return jsonify({
        "msg": "Produto criado com sucesso",
        "id": str(result.inserted_id)
    }), 201


@produtos_bp.route("/produtos", methods=["GET"])
def listar_produtos():

    produtos = []

    for produto in produtos_collection.find():

        produto["_id"] = str(produto["_id"])

        if produto.get("tipoProdutoId"):
            produto["tipoProdutoId"] = str(produto["tipoProdutoId"])

        produtos.append(produto)

    return jsonify(produtos)


@produtos_bp.route("/produtos/<id>", methods=["GET"])
def buscar_produto(id):

    try:

        produto = produtos_collection.find_one({
            "_id": ObjectId(id)
        })

    except:

        return jsonify({
            "erro": "ID inválido"
        }), 400

    if not produto:

        return jsonify({
            "erro": "Produto não encontrado"
        }), 404

    produto["_id"] = str(produto["_id"])

    if produto.get("tipoProdutoId"):
        produto["tipoProdutoId"] = str(produto["tipoProdutoId"])

    return jsonify(produto)

@produtos_bp.route("/produtos/<id>/preco", methods=["PUT"])
def atualizar_preco(id):

    data = request.json

    try:

        result = produtos_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "precoBase": float(data["precoBase"])
            }}
        )

    except:

        return jsonify({
            "erro": "ID inválido"
        }), 400

    if result.matched_count == 0:

        return jsonify({
            "erro": "Produto não encontrado"
        }), 404

    return jsonify({
        "msg": "Preço atualizado"
    })


@produtos_bp.route("/produtos/<id>/status", methods=["PUT"])
def alterar_status(id):

    data = request.json

    try:

        result = produtos_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "ativo": data["ativo"]
            }}
        )

    except:

        return jsonify({
            "erro": "ID inválido"
        }), 400

    if result.matched_count == 0:

        return jsonify({
            "erro": "Produto não encontrado"
        }), 404

    return jsonify({
        "msg": "Status atualizado"
    })