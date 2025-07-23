#!/usr/bin/env python3
"""
Script para testar as correções do frontend
Verifica se os erros '[object Object]' foram resolvidos
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

def test_error_handling():
    """Testa se os erros estão sendo tratados corretamente"""
    print("\n=== Testando Tratamento de Erros ===")
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    
    # Teste 1: Campos vazios (deve retornar erro 400 com mensagem clara)
    print("\n1. Testando campos vazios:")
    data_empty = {
        'script': '',
        'image_prompts': '',
        'voice_provider': 'elevenlabs',
        'voice_type': 'narrator',
        'language': 'pt',
        'video_format': 'tiktok',
        'effects_preset': 'professional',
        'enable_effects': True,
        'image_preset': '3d_cartoon'
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate-video",
            headers=headers,
            json=data_empty
        )
        
        print(f"Status: {response.status_code}")
        if response.headers.get('content-type', '').startswith('application/json'):
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            # Verificar se a estrutura de erro está correta
            if 'error' in response_data:
                error = response_data['error']
                if isinstance(error, dict) and 'message' in error:
                    print("✅ Estrutura de erro correta")
                    print(f"Mensagem: {error['message']}")
                    
                    if 'details' in error and 'field_errors' in error['details']:
                        field_errors = error['details']['field_errors']
                        print(f"Erros de campo: {field_errors}")
                        print("✅ Detalhes de validação presentes")
                else:
                    print("❌ Estrutura de erro incorreta")
            else:
                print("❌ Campo 'error' não encontrado")
        else:
            print(f"Response text: {response.text}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    # Teste 2: Campos faltando (deve retornar erro 400)
    print("\n2. Testando campos faltando:")
    data_missing = {
        'voice_provider': 'elevenlabs',
        'voice_type': 'narrator',
        'language': 'pt',
        'video_format': 'tiktok',
        'effects_preset': 'professional',
        'enable_effects': True,
        'image_preset': '3d_cartoon'
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate-video",
            headers=headers,
            json=data_missing
        )
        
        print(f"Status: {response.status_code}")
        if response.headers.get('content-type', '').startswith('application/json'):
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"Response text: {response.text}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    # Teste 3: Image preset inválido (deve retornar erro 400)
    print("\n3. Testando image preset inválido:")
    data_invalid_preset = {
        'script': 'Teste de script válido com mais de 50 caracteres para passar na validação',
        'image_prompts': 'Scene 1: Teste de prompt válido com mais de 50 caracteres para passar na validação',
        'voice_provider': 'elevenlabs',
        'voice_type': 'narrator',
        'language': 'pt',
        'video_format': 'tiktok',
        'effects_preset': 'professional',
        'enable_effects': True,
        'image_preset': 'invalid_preset'  # Preset inválido
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate-video",
            headers=headers,
            json=data_invalid_preset
        )
        
        print(f"Status: {response.