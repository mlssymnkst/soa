from flask import Blueprint, request, jsonify
from banco import insumos_collection
from bson import ObjectId

insumos_bp = Blueprint("insumos", __name__)

@insumos_bp.route("/insumos", methods=["POST"])
def criar_isumo():
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

@insumos_bp.route('/insumos', methods=['GET '])
def listar_insumos():
    insumos =[]

    for insumo in insumos_collection.fin():
       