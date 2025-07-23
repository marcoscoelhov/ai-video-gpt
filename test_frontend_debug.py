#!/usr/bin/env python3
"""
Script para testar especificamente o problema do frontend
"""

import requests
import json
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
API_BASE_URL = "http://localhost:5000/api"
API_KEY = os.getenv('API_KEY')

def test_with_valid_data():
    """Testa com dados válidos como o frontend deveria enviar"""
    print("\n=== Testando com dados válidos ===")
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    # Dados exatamente como o frontend deveria enviar
    data = {
        'script': 'Liam (Civilian Teen) – Voice: Adam\nMy laundry machine just screamed at me.',
        'image_prompts': 'Scene 1:\n"A 3D cartoon teenager standing in front of a laundry machine in a modern laundry room"',
        'voice_provider': 'elevenlabs',
        'voice_type': 'narrator',
        'language': 'pt',
        'video_format': 'tiktok',
        'effects_preset': 'professional',
        'enable_effects': True,
        'image_preset': '3d_cartoon'  # Valor válido em vez de string vazia
    }
    
    print(f"Dados enviados:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate-video",
            headers=headers,
            json=data
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            return response.status_code == 200
        else:
            print(f"Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"Erro: {e}")
        return False

def test_with_empty_data():
    """Testa com dados vazios para reproduzir o erro"""
    print("\n=== Testando com dados vazios (reproduzir erro) ===")
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    # Dados vazios como pode estar acontecendo no frontend
    data = {
        'script': '',
        'image_prompts': '',
        'voice_provider': 'elevenlabs',
        'voice_type': 'narrator',
        'language': 'pt',
        'video_format': 'tiktok',
        'effects_preset': 'professional',
        'enable_effects': True,
        'image_preset': '3d_cartoon'  # Valor válido para focar no erro dos campos obrigatórios
    }
    
    print(f"Dados enviados:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate-video",
            headers=headers,
            json=data
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            return response.status_code == 400  # Esperamos erro 400
        else:
            print(f"Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"Erro: {e}")
        return False

def test_with_missing_fields():
    """Testa com campos faltando"""
    print("\n=== Testando com campos faltando ===")
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    # Dados sem os campos obrigatórios
    data = {
        'voice_provider': 'elevenlabs',
        'voice_type': 'narrator',
        'language': 'pt',
        'video_format': 'tiktok',
        'effects_preset': 'professional',
        'enable_effects': True,
        'image_preset': '3d_cartoon'  # Valor válido para focar no erro dos campos obrigatórios
    }
    
    print(f"Dados enviados:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate-video",
            headers=headers,
            json=data
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            return response.status_code == 400  # Esperamos erro 400
        else:
            print(f"Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"Erro: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("=== TESTE DE DEBUG DO FRONTEND ===")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"API Key configurada: {'Sim' if API_KEY else 'Não'}")
    
    # Executa os testes
    test1 = test_with_valid_data()
    test2 = test_with_empty_data()
    test3 = test_with_missing_fields()
    
    print("\n=== RESUMO DOS TESTES ===")
    print(f"Teste com dados válidos: {'✓' if test1 else '✗'}")
    print(f"Teste com dados vazios: {'✓' if test2 else '✗'}")
    print(f"Teste com campos faltando: {'✓' if test3 else '✗'}")
    
if __name__ == "__main__":
    main()