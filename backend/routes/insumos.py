from flask import Blueprint, request, jsonify
from banco import insumos_collection
from bson import ObjectId

insumos_bp = Blueprint("insumos", __name__)

#Insumos da empresa
@insumos_bp.route("/insumos", methods=["POST"])
def criar_insumo():
    data = request.json

    if not data.get("categoria") or not data.get("preco_unitario"):
        return jsonify({
            'erro': 'Campo obrigatórios: categoria, preco_unitario'
        }), 400
    
    insumo = {
        'categoria': data['categoria'],
        'preco_unitario': data['preco_unitario'],
        'estoque_disponivel': data.get('estoque_disponivel', 0),
        'unidade_medida': data.get('unidade_medida', 'unidade')
    }

    result = insumos_collection.insert_one(insumo)

    return jsonify({
        'msg': 'insumo criado com sucesso',
        'id': str(result.inserted_id)
    })

#Listar todos os insumos da empresa
@insumos_bp.route('/insumos', methods=['GET'])
def listar_insumos():
    insumos =[]

    for insumo in insumos_collection.find():
        insumo["_id"] = str(insumo["_id"])
        insumos.append(insumo)

    return jsonify(insumos)
#----------------------------------------------------#

#Vai trazer um insumo por ID
@insumos_bp.route("/insumos/<id>", methods=["GET"])
def buscar_insumo(id):
    try:
        insumo = insumos_collection.find_one({
            "_id": ObjectId(id)
        })
    except:
        return jsonify({
            "erro": "ID inválido"
        }), 400
    
    if not insumo:
        return jsonify({
            "erro": "Insumo não encontrado"
        }), 404
    
    insumo["_id"] = str(insumo["_id"])
    return jsonify(insumo)
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
