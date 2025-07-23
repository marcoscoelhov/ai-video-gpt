#!/usr/bin/env python3
"""
Script de debug para testar a API do AI Video GPT
"""

import requests
import json
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

API_BASE_URL = 'http://localhost:5000/api'
API_KEY = os.getenv('API_KEY', '7ffb1add-a5c8-4e47-b6ec-8c9a8f630aae')

def test_endpoint(endpoint, method='GET', data=None, headers=None):
    """Testar um endpoint específico"""
    url = f"{API_BASE_URL}{endpoint}"
    
    default_headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    if headers:
        default_headers.update(headers)
    
    print(f"\n🔍 Testando {method} {url}")
    print(f"📋 Headers: {default_headers}")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=default_headers)
        elif method == 'POST':
            response = requests.post(url, headers=default_headers, json=data)
        else:
            print(f"❌ Método {method} não suportado")
            return False
        
        print(f"📊 Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📄 Response (text): {response.text[:500]}")
        
        return response.status_code < 400
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print("🚀 Iniciando testes da API AI Video GPT")
    print(f"🔑 API Key: {API_KEY[:10]}...{API_KEY[-4:]}")
    
    # Teste 1: Health check
    print("\n" + "="*50)
    print("TESTE 1: Health Check")
    test_endpoint('/health')
    
    # Teste 2: Auth info
    print("\n" + "="*50)
    print("TESTE 2: Auth Info")
    test_endpoint('/auth/info')
    
    # Teste 3: Auth validate
    print("\n" + "="*50)
    print("TESTE 3: Auth Validate")
    test_endpoint('/auth/validate', 'POST')
    
    # Teste 4: Image presets
    print("\n" + "="*50)
    print("TESTE 4: Image Presets")
    test_endpoint('/image-presets')
    
    # Teste 5: Generate video (dados mínimos)
    print("\n" + "="*50)
    print("TESTE 5: Generate Video (dados de teste)")