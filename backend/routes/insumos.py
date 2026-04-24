from flask import Blueprint, request, jsonify
from banco import insumos_collection
from bson import ObjectId

insumos_bp = Blueprint("insumos", __name__)

#Listar todos ou filtrar por categoria
@insumos_bp.route("/insumos", methods=["GET"])
def listar_insumos():
    categoria = request.args.get("categoria")

    filtro = {}

    if categoria:
        filtro["categoria"] = {
            "$regex": categoria.strip(),
            "$options": "i"
        }

    insumos = []

    for insumo in insumos_collection.find(filtro):
        insumo["_id"] = str(insumo["_id"])
        insumos.append(insumo)

    return jsonify(insumos)


#Insumos da empresa
@insumos_bp.route("/insumos", methods=["POST"])
def criar_insumo():
    data = request.json

    if not data.get("categoria") or not data.get("preco_unitario"):
        return jsonify({
            'erro': 'Campo obrigatórios: categoria, preco_unitario'
        }), 400
    
    insumo = {
        'categoria': data['categoria'].lower(),
        'preco_unitario': data['preco_unitario'],
        'estoque_disponivel': data.get('estoque_disponivel', 0),
        'unidade_medida': data.get('unidade_medida', 'unidade')
    }

    result = insumos_collection.insert_one(insumo)

    return jsonify({
        'msg': 'insumo criado com sucesso',
        'id': str(result.inserted_id)
    })

#----------------------------------------------------#


# Atualiza os dados dos insumos
@insumos_bp.route("/insumos/<id>", methods=["PUT"])
def atualizar_insumos(id):
    data = request.json

    if "estoque_disponivel" in data:
        return jsonify({
            "erro": "Estoque não pode ser alterado por aqui"
        }),400

    try:
        result = insumos_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )

    except:
        return jsonify({
            "erro": "ID inválido"
        }), 400
    
    if result.matched_count == 0:
        return jsonify({
            "erro": "Insumo não encontrado"
        }), 404
       
    return jsonify({
        "msg": "Insumo atualizado com sucesso"
    })
#----------------------------------------------------#

#Deletando
@insumos_bp.route("/insumos/<id>", methods=["DELETE"])
def deletar_insumo(id):
    try:
        result = insumos_collection.delete_one({
            "_id": ObjectId(id)
        })
    except:
        return jsonify({
            "erro": "Insumo não encontrado"
        }), 404
    
    if result.deleted_count == 0:
        return jsonify({
            "erro": "Insumo não encontrado"
        }), 404
    
    return jsonify({
        "msg": "Insumo deletado com sucesso"
    })
