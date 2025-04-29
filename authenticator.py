from flask import request, jsonify
import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def protected():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify(message="Token é necessário!"), 403

    parts = auth_header.split()
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        return jsonify(message="Cabeçalho de autorização malformado!"), 401
    token = parts[1]

    try:
        # Decodifica o token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify(message=f"Bem-vindo, {decoded['user']}!")
    except jwt.ExpiredSignatureError:
        return jsonify(message="Token expirado! Faça login novamente."), 401
    except jwt.InvalidTokenError:
        return jsonify(message="Token inválido!"), 403