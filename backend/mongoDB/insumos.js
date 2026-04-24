use('SOA')

db.insumos.insertMany([
    {
        categoria: "papel_impressao",
        modelo: "Concetto Bianco",
        altura: 21,
        largura: 29.7,
        peso: 170,
        preco_venda: 25.9,
        estoque_disponivel: 100,
        unidade_medida: "folhas"
    },

    {
        categoria: "papel_impressao",
        modelo: "Vergê Diamente",
        altura: 21,
        largura: 29.7,
        peso: 180,
        preco_venda: 22.9,
        estoque_disponivel: 80,
        unidade_medida: "folhas"
    },

    {
        categoria: "Envelope",
        modelo: "Luva",
        altura: 21.3,
        largura: 15.5,
        cor: "Kraf",
        preco_venda: 8.5,
        estoque_disponivel: 50,
        unidade_medida: "unidade"
    },

    {
        categoria: "aviamento",
        modelo: "Fita de Cetim",
        metros_por_rolo: 10,
        preco_venda: 12.0,
        estoque_disponivel: 20,
        unidade_medida: "rolo"
    }
])