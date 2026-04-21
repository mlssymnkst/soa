use('SOA')
db.getCollection('insumos').insertOne({
    "categoria": "Papel",
    "preco_unitario": 25.90,
    "estoque_disponivel": 100,
    "unidade_medida": "folhas"
})

use('SOA')
db.insumos.find()

