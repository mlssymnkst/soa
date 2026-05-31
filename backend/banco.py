from pymongo import MongoClient 

client = MongoClient("mongodb://localhost:27017/projetoIntegrador")
db = client["SOA"]

clientes_collection = db["clientes"]
produtos_collection = db["produtos"]
insumos_collection = db["insumos"]
orcamentos_collection = db["orcamentos"]
tipos_produto_collection = db["tipos_produto"]
itens_orcamento_collection = db["itens_orcamento"]
modelos_personalizados_collection = db["modelos_personalizados"]
