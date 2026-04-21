from pymongo import MongoClient 

client = MongoClient("mongodb://localhost:27017/projetoIntegrador")
db = client["SOA"]

clientes_collection = db["clientes"]
produtos_collection = db["produtos"]
insumos_collection = db["insumos"]
orcamentos_collection = db["orcamentos"]