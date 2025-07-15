#!/usr/bin/env python3
"""
Demo do AI Video GPT com Google Imagen 4

Este script demonstra a nova integração com Google Imagen 4 para geração de imagens.
Requer configuração do Google Cloud Project.
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def check_google_cloud_config():
    """Verifica se o Google Cloud está configurado"""
    load_dotenv()
    
    print("🔍 Verificando configuração do Google Cloud...")
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    if not project_id or project_id == "your_project_id_here":
        print("❌ GOOGLE_CLOUD_PROJECT não configurado no arquivo .env")
        print("   Configure seu Project ID do Google Cloud")
        print("   Exemplo: GOOGLE_CLOUD_PROJECT=meu-projeto-123")
        return False
        
    print(f"✅ Google Cloud Project: {project_id}")
    print(f"✅ Location: {location}")
    
    # Verificar se as credenciais estão configuradas
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("⚠️  GOOGLE_APPLICATION_CREDENTIALS não configurado")
        print("   Você pode usar Application Default Credentials (ADC)")
        print("   Execute: gcloud auth application-default login")
    else:
        print("✅ Credenciais configuradas via GOOGLE_APPLICATION_CREDENTIALS")
    
    return True

def test_imagen_generation():
    """Testa a geração de imagens com Google Imagen"""
    print("\n🎨 Testando geração de imagens com Google Imagen 4...")
    
    try:
        from imagegen import test_image_generation
        test_image_generation()
    except Exception as e:
        print(f"❌ Erro ao testar geração de imagens: {e}")
        return False
    
    return True

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("\n📦 Verificando dependências...")
    
    required_packages = [
        ('vertexai', 'vertexai'),
        ('google.cloud.aiplatform', 'google.cloud.aiplatform'),
        ('google_generativeai', 'google.generativeai')
    ]
    
    missing_packages = []
    
    for display_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name}")
            missing_packages.append(display_name)
    
    if missing_packages:
        print(f"\n⚠️  Instale as dependências faltantes:")
        print(f"pip install -r requirements.txt")
        return False
    
    return True

def show_project_status():
    """Mostra o status geral do projeto"""
    print("\n📊 Status do Projeto AI Video GPT")
    print("=" * 50)
    
    # Verificar arquivos principais
    main_files = [
        'main.py',
        'src/imagegen.py',
        'src/scriptgen.py',
        'src/voice.py',
        'requirements.txt',
        '.env'
    ]
    
    print("\n📁 Arquivos principais:")
    for file in main_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
    
    # Verificar diretórios
    directories = ['src', 'output', 'tasks']
    print("\n📂 Diretórios:")
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/")

def main():
    """Função principal do demo"""
    print("🎬 Demo AI Video GPT - Google Imagen 4")
    print("=" * 50)
    
    # Verificar dependências
    if not check_dependencies():
        print("\n❌ Dependências não atendidas. Execute 'pip install -r requirements.txt'")
        return
    
    # Verificar configuração do Google Cloud
    if not check_google_cloud_config():
        print("\n❌ Configure o Google Cloud antes de continuar.")
        print("\n📋 Passos para configuração:")
        print("1. Crie um projeto no Google Cloud Console")
        print("2. Ative a API Vertex AI")
        print("3. Configure autenticação: gcloud auth application-default login")
        print("4. Adicione GOOGLE_CLOUD_PROJECT=seu-projeto no arquivo .env")
        return
    
    # Testar geração de imagens
    test_imagen_generation()
    
    # Mostrar status do projeto
    show_project_status()
    
    print("\n🎯 Próximos passos:")
    print("1. Configure suas credenciais do Google Cloud")
    print("2. Execute: python demo_google_imagen.py")
    print("3. Para gerar um vídeo completo: python main.py --theme 'seu tema'")
    
    print("\n✨ Integração com Google Imagen 4 concluída!")

if __name__ == "__main__":
    main()