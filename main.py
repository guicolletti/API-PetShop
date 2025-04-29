from flask import Flask, jsonify, redirect, request
from dotenv import load_dotenv
from authenticator import protected
from produtos import products
import jwt
import os
from datetime import datetime, timedelta, timezone

load_dotenv()
app = Flask(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
app.config["SECRET_KEY"] = SECRET_KEY
print(SECRET_KEY)

@app.route('/')
def index():
    return redirect('/login')

@app.route('/produtos', methods=['GET'])
def produtos():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify(message="Token é necessário!"), 403

    parts = auth_header.split()
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        return jsonify(message="Cabeçalho de autorização malformado!"), 401
    token = parts[1]

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify(message="Token expirado! Faça login novamente."), 401
    except jwt.InvalidTokenError:
        return jsonify(message="Token inválido!"), 403

    filtro_asc = request.args.get('filtro_asc', '')
    filtro_desc = request.args.get('filtro_desc', '')
    filtro_descricao = request.args.get('description_part', '')

    dicionario_filtro = [produto for produto in products if filtro_descricao in produto['product_description']]

    if filtro_asc:
        if dicionario_filtro:
            dicionario_filtro = sorted(dicionario_filtro, key=lambda x: x['product_price'], reverse=False)
        else:
            dicionario_filtro = sorted(products, key=lambda x: x['product_price'], reverse=False)

    elif filtro_desc:
        if dicionario_filtro:
            dicionario_filtro = sorted(dicionario_filtro, key=lambda x: x['product_price'], reverse=True)
        else:
            dicionario_filtro = sorted(products, key=lambda x: x['product_price'], reverse=True)

    if dicionario_filtro:
        return jsonify(dicionario_filtro)
    else:
        return jsonify(products)

@app.route('/produtos/<int:id>', methods=['GET'])
def produto_por_id(id):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify(message="Token é necessário!"), 403

    parts = auth_header.split()
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        return jsonify(message="Cabeçalho de autorização malformado!"), 401
    token = parts[1]

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify(products[id-1])
    except jwt.ExpiredSignatureError:
        return jsonify(message="Token expirado! Faça login novamente."), 401
    except jwt.InvalidTokenError:
        return jsonify(message="Token inválido!"), 403

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify(message="Dados de login não fornecidos!"), 400
    if "username" not in data or "password" not in data:
        return jsonify(message="Campos 'username' e 'password' são obrigatórios!"), 400
    if data["username"] == "admin" and data["password"] == "123":
        token = jwt.encode(
            {"user": data["username"], "exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
            SECRET_KEY,
            algorithm="HS256"
        )
        return jsonify(token=token)

    return jsonify(message="Credenciais inválidas!"), 401

if __name__ == '__main__':
    app.run(debug=True)