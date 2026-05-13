from flask import Flask
from flask_cors import CORS
from routes import insumos_bp, orcamentos_bp
from bot_routes import bot_bp 

app = Flask(__name__)
CORS(app)

app.register_blueprint(insumos_bp)
app.register_blueprint(orcamentos_bp)
app.register_blueprint(bot_bp)       

@app.route("/")
def home():
    return {"msg": "API rodando com sucesso"}


if __name__ == "__main__":
    app.run(debug=True)