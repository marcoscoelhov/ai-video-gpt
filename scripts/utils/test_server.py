#!/usr/bin/env python3
"""
Servidor Flask de teste simples para verificar dependências
"""

try:
    from flask import Flask, jsonify
    from flask_cors import CORS
    print("✅ Flask e Flask-CORS importados com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar Flask: {e}")
    exit(1)

app = Flask(__name__)
CORS(app)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'success',
        'message': 'Servidor Flask funcionando!',
        'frontend_url': 'Abra frontend/index.html no navegador'
    })

if __name__ == '__main__':
    print("🚀 Iniciando servidor de teste...")
    print("🌐 Acesse: http://localhost:5000/test")
    app.run(debug=True, host='0.0.0.0', port=5000)