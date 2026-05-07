#arrrumar o nome do usuario, conexões entre a tela e banconosql

from flask import Flask, request, redirect, send_from_directory, session
import psycopg2, os

app = Flask(__name__)
app.secret_key = 'segredo123'

# conexão com PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="lamore",
    user="postgres",
    password="1234",
)

@app.route('/')
def login_page():
    base = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(base, '..', 'login')
    return send_from_directory(caminho, 'html_login.html') # TROCAR O "."

#INSUMOS
@app.route('/insumos')
def insumos():
    base = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(base, '..', 'insumos')

    usuario = session.get('usuario')

    admins = ["haruka", "marly", "admin"]

    if usuario and usuario.lower() in admins:
        role = "admin"
    else:
        role = "user"

    html = open(os.path.join(caminho, 'insumos.html'), encoding='utf-8').read()

    html = html.replace('Usuário 1', usuario if usuario else 'Visitante')

    # 🔥 INJETA ROLE ANTES DO JS
    html = html.replace(
        '<script src="/insumos/insumos.js"></script>',
        f"""
        <script>
            const USER_ROLE = "{role}";
        </script>
        <script src="/insumos/insumos.js"></script>
        """
    )

    return html


#CSS
@app.route('/login/<path:arquivo>')
def arquivos_login(arquivo):
    base = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(base, '..', 'login')
    return send_from_directory(caminho, arquivo)

# css bot 
@app.route('/bot/<path:arquivo>')
def arquivos_bot(arquivo):
    base = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(base, '..', 'bot')
    return send_from_directory(caminho, arquivo)

#imagem 
@app.route('/images/<path:arquivo>')
def imagens(arquivo):
    base = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(base, '..', 'images')
    return send_from_directory(caminho, arquivo)

#chatbot
@app.route('/chatbot')
def chatbot():
    base = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(base, '..', 'bot')
    return send_from_directory(caminho, 'chatbot.html')


#para aparecer o nome em insumos
@app.route('/login_session', methods=['POST'])
def login_session():
    from flask import session

    usuario = request.form['login']
    senha = request.form['senha']

    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM entrada WHERE usuario = %s AND senha = %s",
        (usuario, senha)
    )
    result = cursor.fetchone()

    if result:
        session['usuario'] = usuario  # 🔥 AQUI salva de verdade
        return redirect('/insumos')
    else:
        return "Login inválido"

#inusmos


#css insumos
@app.route('/insumos/<path:arquivo>')
def arquivos_insumos(arquivo):
    base = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(base, '..', 'insumos')
    return send_from_directory(caminho, arquivo)

app.run(debug=True)