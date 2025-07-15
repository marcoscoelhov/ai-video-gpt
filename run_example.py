#!/usr/bin/env python3
"""
Script de exemplo para executar o AI Video GPT

Antes de executar:
1. Configure suas chaves de API no arquivo .env
2. Instale as dependências: pip install -r requirements.txt
3. Execute: python run_example.py
"""

import os
from dotenv import load_dotenv

def check_environment():
    """Verifica se o ambiente está configurado corretamente"""
    load_dotenv()
    
    print("🔍 Verificando configuração do ambiente...")
    
    # Verificar chaves de API
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY não configurada no arquivo .env")
        print("   Obtenha sua chave em: https://makersuite.google.com/app/apikey")
        return False
        
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY não configurada no arquivo .env")
        print("   Obtenha sua chave em: https://platform.openai.com/api-keys")
        return False
    
    print("✅ Chaves de API configuradas")
    
    # Verificar dependências
    try:
        import google.generativeai
        import dotenv
        print("✅ Dependências básicas instaladas")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("   Execute: pip install -r requirements.txt")
        return False
    
    return True

def run_video_generation(theme="Cyberpunk city exploration"):
    """Executa a geração de vídeo"""
    if not check_environment():
        print("\n⚠️  Configure o ambiente antes de continuar.")
        return
    
    print(f"\n🎬 Iniciando geração de vídeo para o tema: '{theme}'")
    print("\n📋 Executando comando:")
    print(f"python main.py --theme \"{theme}\"")
    
    # Importar e executar o main
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from main import main
        main(theme)
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        print("\nVerifique:")
        print("1. Se as chaves de API estão corretas")
        print("2. Se você tem créditos nas APIs")
        print("3. Se todas as dependências estão instaladas")

if __name__ == "__main__":
    print("🤖 AI Video GPT - Script de Exemplo")
    print("=" * 40)
    
    # Verificar se o arquivo .env existe
    if not os.path.exists(".env"):
        print("❌ Arquivo .env não encontrado!")
        print("   Um arquivo .env básico foi criado. Configure suas chaves de API.")
        exit(1)
    
    run_video_generation()