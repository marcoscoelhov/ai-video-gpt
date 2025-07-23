#!/usr/bin/env python3
"""
Script de debug para testar a geração de vídeo e identificar problemas
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
API_BASE_URL = "http://localhost:5000"
API_KEY = os.getenv('API_KEY')

def test_auth_info():
    """Testa o endpoint de informações de autenticação"""
    print("\n=== Testando /api/auth/info ===")
    try:
        response = requests.get(f"{API_BASE_URL}/api/auth/info")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

def test_api_key_validation():
    """Testa a validação da API key"""
    print("\n=== Testando validação da API key ===")
    try:
        headers = {'X-API-Key': API_KEY}
        response = requests.post(f"{API_BASE_URL}/api/auth/validate", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro: {e}")
        return False

def test_video_generation():
    """Testa a geração de vídeo com dados mínimos"""
    print("\n=== Testando geração de vídeo ===")
    try:
        headers = {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        }
        
        data = {
            'prompt': 'Um gato brincando no jardim',
            'duration': 5,
            'aspect_ratio': '16:9'
        }
        
        print(f"Enviando dados: {json.dumps(data, indent=2)}")
        print(f"Headers: {headers}")
        
        response = requests.post(
            f"{API_BASE_URL}/api/generate-video", 
            headers=headers,
            json=data
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers da resposta: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response text: {response.text}")
        
        return response.status_code == 200, response
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return False, None

def test_frontend_request():
    """Simula uma requisição como o frontend faria"""
    print("\n=== Simulando requisição do frontend ===")
    try:
        # Simular exatamente como o frontend faz
        url = f"{API_BASE_URL}/api/generate-video"
        
        # Headers como o frontend envia
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        # Dados como o frontend envia
        data = {
            'prompt': 'Teste de debug do frontend',
            'duration': 5,
            'aspect_ratio': '16:9',
            'voice_id': 'adam',
            'image_preset': 'none'
        }
        
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, headers=headers, json=data)
        
        print(f"\nResposta:")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                response_data = response.json()
                print(f"JSON: {json.dumps(response_data, indent=2)}")
                return response.status_code == 200, response_data
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON: {e}")
                print(f"Texto da resposta: {response.text}")
        else:
            print(f"Resposta não é JSON: {response.text}")
        
        return False, None
        
    except Exception as e:
        print(f"Erro na requisição: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def main():
    """Função principal de debug"""
    print("=== DEBUG DA GERAÇÃO DE VÍDEO ===")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-4:] if API_KEY else 'None'}")
    
    if not API_KEY:
        print("\n❌ ERRO: API_KEY não encontrada no arquivo .env")
        return
    
    # Teste 1: Informações de autenticação
    auth_ok = test_auth_info()
    
    # Teste 2: Validação da API key
    if auth_ok:
        key_ok = test_api_key_validation()
    else:
        print("\n⚠️ Pulando teste de API key devido a erro anterior")
        key_ok = False
    
    # Teste 3: Geração de vídeo básica
    if key_ok:
        video_ok, response = test_video_generation()
    else:
        print("\n⚠️ Pulando teste de geração devido a erro anterior")
        video_ok = False
    
    # Teste 4: Simulação do frontend
    frontend_ok, frontend_response = test_frontend_request()
    
    # Resumo
    print("\n=== RESUMO DOS TESTES ===")
    print(f"✅ Auth Info: {'OK' if auth_ok else 'FALHOU'}")
    print(f"✅ API Key: {'OK' if key_ok else 'FALHOU'}")
    print(f"✅ Geração de Vídeo: {'OK' if video_ok else 'FALHOU'}")
    print(f"✅ Simulação Frontend: {'OK' if frontend_ok else 'FALHOU'}")
    
    if not any([auth_ok, key_ok, video_ok, frontend_ok]):
        print("\n❌ TODOS OS TESTES FALHARAM - Verifique se o servidor está rodando")
    elif not frontend_ok:
        print("\n⚠️ PROBLEMA NO FRONTEND - Os erros [object Object] podem estar relacionados ao tratamento de resposta")

if __name__ == "__main__":
    main()