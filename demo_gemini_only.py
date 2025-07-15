#!/usr/bin/env python3
"""
Demo do AI Video GPT usando apenas a API do Gemini

Este script demonstra como o projeto funciona usando apenas o Gemini,
sem necessidade da API do OpenAI para funcionalidades básicas.
"""

import os
import sys
from dotenv import load_dotenv

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def check_gemini_only():
    """Verifica se o Gemini está configurado"""
    load_dotenv()
    
    print("🔍 Verificando configuração do Gemini...")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY não configurada no arquivo .env")
        print("\n📋 Para configurar:")
        print("1. Acesse: https://makersuite.google.com/app/apikey")
        print("2. Crie uma conta Google (se necessário)")
        print("3. Gere uma nova chave de API")
        print("4. Edite o arquivo .env e substitua 'your_gemini_api_key_here' pela sua chave")
        return False
        
    print("✅ GEMINI_API_KEY configurada")
    
    # Verificar dependências básicas
    try:
        import google.generativeai
        print("✅ google-generativeai instalado")
    except ImportError:
        print("❌ google-generativeai não instalado")
        print("   Execute: pip install google-generativeai")
        return False
    
    return True

def test_script_generation():
    """Testa apenas a geração de roteiro com Gemini"""
    if not check_gemini_only():
        return
    
    print("\n🎬 Testando geração de roteiro...")
    
    try:
        from scriptgen import generate_script
        
        theme = "Uma aventura espacial"
        print(f"Tema: {theme}")
        
        script_data = generate_script(theme)
        
        if script_data:
            print("\n✅ Roteiro gerado com sucesso!")
            print(f"Título: {script_data.get('title', 'N/A')}")
            print(f"Número de cenas: {len(script_data.get('scenes', []))}")
            
            # Mostrar primeira cena como exemplo
            if script_data.get('scenes'):
                first_scene = script_data['scenes'][0]
                print(f"\nPrimeira cena:")
                print(f"  Descrição visual: {first_scene.get('visual_description', 'N/A')[:100]}...")
                print(f"  Narração: {first_scene.get('narration', 'N/A')[:100]}...")
        else:
            print("❌ Falha na geração do roteiro")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\nVerifique se:")
        print("- A chave do Gemini está correta")
        print("- Você tem acesso à API do Gemini")
        print("- Sua conexão com a internet está funcionando")

def show_project_status():
    """Mostra o status atual do projeto"""
    print("\n📊 Status do Projeto AI Video GPT")
    print("=" * 40)
    
    # Verificar arquivos principais
    files_to_check = [
        "main.py",
        "src/scriptgen.py",
        "src/imagegen.py", 
        "src/voice.py",
        "src/assemble.py",
        ".env",
        "requirements.txt"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
    
    print("\n🔧 Funcionalidades:")
    print("✅ Geração de roteiro (Gemini)")
    print("⚠️  Geração de imagens (requer configuração adicional)")
    print("✅ Geração de voz (gTTS - gratuito)")
    print("✅ Montagem de vídeo (MoviePy)")
    print("⚠️  Upload automático (requer OpenAI para algumas funções)")
    
    print("\n📋 Próximos passos:")
    print("1. Configure GEMINI_API_KEY no arquivo .env")
    print("2. Execute: python demo_gemini_only.py")
    print("3. Para funcionalidade completa, configure também OPENAI_API_KEY")

if __name__ == "__main__":
    print("🤖 AI Video GPT - Demo Gemini")
    print("=" * 35)
    
    if not os.path.exists(".env"):
        print("❌ Arquivo .env não encontrado!")
        exit(1)
    
    show_project_status()
    
    print("\n" + "=" * 35)
    test_script_generation()