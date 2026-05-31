use('SOA')

// // IDs fixos para relacionamentos
// const tipoConviteId = ObjectId()
// const tipoTagId = ObjectId()
// const tipoCardapioId = ObjectId()

// const produtoConvitePremiumId = ObjectId()
// const produtoConviteFloralId = ObjectId()
// const produtoTagId = ObjectId()
// const produtoCardapioId = ObjectId()

// const clienteVictorId = ObjectId()
// const clienteAnnaId = ObjectId()
// const clienteMarianaId = ObjectId()

// const orcamentoVictorId = ObjectId()
// const orcamentoAnnaId = ObjectId()



// TIPOS DE PRODUTO
db.tipos_produto.insertMany([
    {
        _id: tipoConviteId,
        nome: "Convites",
        descricao: "Produtos voltados para convites personalizados de eventos",
        ativo: true
    },
    {
        _id: tipoTagId,
        nome: "Tags",
        descricao: "Tags personalizadas para lembranças e brindes",
        ativo: true
    },
    {
        _id: tipoCardapioId,
        nome: "Cardápios",
        descricao: "Cardápios personalizados para mesas e eventos",
        ativo: true
    }
])

// PRODUTOS
db.produtos.insertMany([
    {
        _id: produtoConvitePremiumId,
        nome: "Convite Casamento Premium",
        descricao: "Convite com acabamento premium para casamento",
        precoBase: 12.5,
        ativo: true,
        tipoProdutoId: tipoConviteId
    },
    {
        _id: produtoConviteFloralId,
        nome: "Convite Floral Luxo",
        descricao: "Convite floral personalizado com acabamento sofisticado",
        precoBase: 18.5,
        ativo: true,
        tipoProdutoId: tipoConviteId
    },
    {
        _id: produtoTagId,
        nome: "Tag Personalizada",
        descricao: "Tag personalizada para lembranças e brindes",
        precoBase: 3.5,
        ativo: true,
        tipoProdutoId: tipoTagId
    },
    {
        _id: produtoCardapioId,
        nome: "Cardápio de Mesa",
        descricao: "Cardápio personalizado para eventos",
        precoBase: 9.9,
        ativo: true,
        tipoProdutoId: tipoCardapioId
    }
])

// INSUMOS
db.insumos.insertMany([
    {
        categoria: "papel_impressao",
        modelo: "Concetto Bianco",
        altura: 21,
        largura: 29.7,
        peso: 170,
        aproveitamento: 4,
        preco_venda: 25.9,
        peso_por_folha_g: 18.5,
        estoque_disponivel: 100,
        unidade_medida: "folhas"
    },
    {
        categoria: "papel_impressao",
        modelo: "Vergê Diamante",
        altura: 21,
        largura: 29.7,
        peso: 180,
        aproveitamento: 2,
        preco_venda: 22.9,
        peso_por_folha_g: 20,
        estoque_disponivel: 80,
        unidade_medida: "folhas"
    },
    {
        categoria: "papel",
        modelo: "Couchê 115g",
        aproveitamento: 4,
        preco_venda: 0.35,
        peso_por_folha_g: 18.5,
        estoque_disponivel: 500,
        unidade_medida: "folhas"
    },
    {
        categoria: "papel",
        modelo: "Couchê 300g",
        aproveitamento: 2,
        preco_venda: 0.9,
        peso_por_folha_g: 48,
        estoque_disponivel: 300,
        unidade_medida: "folhas"
    },
    {
        categoria: "Envelope",
        modelo: "Envelope Kraft",
        altura: 21.3,
        largura: 15.5,
        cor: "Kraft",
        preco_venda: 8.5,
        estoque_disponivel: 50,
        unidade_medida: "unidade"
    },
    {
        categoria: "Envelope",
        modelo: "Envelope Branco",
        altura: 21.3,
        largura: 15.5,
        cor: "Branco",
        preco_venda: 7.5,
        estoque_disponivel: 70,
        unidade_medida: "unidade"
    },
    {
        categoria: "fita",
        modelo: "Fita Cetim 1cm",
        metros_por_rolo: 10,
        preco_venda: 12.0,
        preco_por_cm: 0.012,
        estoque_disponivel: 20,
        unidade_medida: "rolo"
    },
    {
        categoria: "fita",
        modelo: "Fita Veludo 1cm",
        metros_por_rolo: 10,
        preco_venda: 18.0,
        preco_por_cm: 0.02,
        estoque_disponivel: 15,
        unidade_medida: "rolo"
    }
])

// CLIENTES
db.clientes.insertMany([
    {
        _id: clienteVictorId,
        nome: "Victor Ramon",
        telefone: "11999999999",
        email: "victor@email.com",
        endereco: "Rua Comandante Taylor, São Paulo - SP",
        tipoCliente: "comum",
        dataCadastro: new Date()
    },
    {
        _id: clienteAnnaId,
        nome: "Anna Valentina",
        telefone: "11988888888",
        email: "anna@email.com",
        endereco: "Rua dos Cabeçudos, São Paulo - SP",
        tipoCliente: "comum",
        dataCadastro: new Date()
    },
    {
        _id: clienteMarianaId,
        nome: "Mariana Souza",
        telefone: "11977777777",
        email: "mariana@email.com",
        endereco: "Av. Paulista, 1000 - São Paulo - SP",
        tipoCliente: "premium",
        dataCadastro: new Date()
    }
])

// MODELOS PERSONALIZADOS
db.modelos_personalizados.insertMany([
    {
        nomeModelo: "Convite Floral Luxo",
        tipoPersonalizacao: "Floral com fita cetim",
        descricao: "Modelo com arte floral, papel couchê e acabamento em fita",
        valorTotal: 17.5,
        dataCriacao: new Date()
    },
    {
        nomeModelo: "Convite Clássico Minimalista",
        tipoPersonalizacao: "Minimalista com envelope branco",
        descricao: "Modelo elegante com poucos elementos visuais",
        valorTotal: 12.0,
        dataCriacao: new Date()
    },
    {
        nomeModelo: "Tag Lembrança Dourada",
        tipoPersonalizacao: "Tag com detalhe dourado",
        descricao: "Tag personalizada para lembranças de casamento",
        valorTotal: 4.5,
        dataCriacao: new Date()
    }
])

// ORÇAMENTOS
db.orcamentos.insertMany([
    {
        _id: orcamentoVictorId,
        clienteId: clienteVictorId.toString(),
        clienteNome: "Victor Ramon",
        session_id: "sessao-demo-001",
        itens: [
            {
                produto: "Convite Casamento Premium",
                produtoId: produtoConvitePremiumId.toString(),
                quantidade: 250,
                envelope: "Envelope Branco",
                tamanho_impressao: "148x210",
                papel: "Couchê 300g",
                aproveitamento: 2,
                qtde_folhas: 125,
                custo_papel: 112.5,
                peso_g: 6000,
                insumo_id: "",
                fita: null,
                custo_fita: 0
            }
        ],
        endereco: "Rua Comandante Taylor, São Paulo - SP",
        frete: {
            valor: 36.0,
            prazo_dias: 5,
            transportadora: "A definir",
            origem: "simulado"
        },
        valor_total: 148.5,
        criado_em: new Date(),
        status: "finalizado"
    },
    {
        _id: orcamentoAnnaId,
        clienteId: clienteAnnaId.toString(),
        clienteNome: "Anna Valentina",
        session_id: "sessao-demo-002",
        itens: [
            {
                produto: "Convite Floral Luxo",
                produtoId: produtoConviteFloralId.toString(),
                quantidade: 100,
                envelope: "Envelope Kraft",
                tamanho_impressao: "10x15",
                papel: "Couchê 115g",
                aproveitamento: 4,
                qtde_folhas: 25,
                custo_papel: 8.75,
                peso_g: 462.5,
                insumo_id: "",
                fita: "Fita Cetim 1cm",
                custo_fita: 36
            }
        ],
        endereco: "Rua dos Cabeçudos, São Paulo - SP",
        frete: {
            valor: 16.62,
            prazo_dias: 5,
            transportadora: "A definir",
            origem: "simulado"
        },
        valor_total: 61.37,
        criado_em: new Date(),
        status: "finalizado"
    }
])

// ITENS DE ORÇAMENTO
db.itens_orcamento.insertMany([
    {
        orcamentoId: orcamentoVictorId.toString(),
        produtoId: produtoConvitePremiumId.toString(),
        produtoNome: "Convite Casamento Premium",
        quantidade: 250,
        precoUnitario: 12.5,
        subtotal: 3125,
        tempoEntrega: 7,
        valorFrete: 36.0
    },
    {
        orcamentoId: orcamentoAnnaId.toString(),
        produtoId: produtoConviteFloralId.toString(),
        produtoNome: "Convite Floral Luxo",
        quantidade: 100,
        precoUnitario: 18.5,
        subtotal: 1850,
        tempoEntrega: 5,
        valorFrete: 16.62
    }
])