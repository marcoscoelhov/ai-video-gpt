#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificador de Dependências - AI Video GPT

Este script verifica se todas as dependências necessárias estão instaladas
e fornece instruções de instalação quando necessário.
"""

import subprocess
import sys
import os
from pathlib import Path

# Carrega variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv não encontrado. Algumas verificações podem falhar.")

def check_command_exists(command):
    """Verifica se um comando está disponível no sistema."""
    try:
        # Validate command name to prevent injection
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+$', command):
            return False
        
        # Use secure subprocess call
        result = subprocess.run([command, "-version"], 
                              capture_output=True, 
                              check=False,  # Don't raise on non-zero exit
                              timeout=10,
                              text=True,
                              shell=False)  # Never use shell
        
        # Command exists if it runs without FileNotFoundError
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    except Exception:
        return False

def check_python_package(package_name):
    """Verifica se um pacote Python está instalado."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def print_header(title):
    """Imprime cabeçalho formatado."""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def print_status(item, status, details=""):
    """Imprime status de uma verificação."""
    icon = "✅" if status else "❌"
    print(f"{icon} {item}")
    if details:
        print(f"   {details}")

def check_system_dependencies():
    """Verifica dependências do sistema."""
    print_header("Dependências do Sistema")
    
    dependencies = {
        "FFmpeg": "ffmpeg",
        "FFprobe": "ffprobe"
    }
    
    all_good = True
    
    for name, command in dependencies.items():
        exists = check_command_exists(command)
        print_status(name, exists)
        if not exists:
            all_good = False
    
    return all_good

def check_python_dependencies():
    """Verifica dependências Python."""
    print_header("Dependências Python")
    
    dependencies = {
        "PIL (Pillow)": "PIL",
        "Google GenAI": "google.genai",
        "Python-dotenv": "dotenv",
        "Requests": "requests"
    }
    
    all_good = True
    
    for name, package in dependencies.items():
        exists = check_python_package(package)
        print_status(name, exists)
        if not exists:
            all_good = False
    
    return all_good

def check_environment_variables():
    """Verifica variáveis de ambiente necessárias."""
    print_header("Variáveis de Ambiente")
    
    env_vars = {
        "GEMINI_API_KEY": "Chave da API do Google Gemini",
        "OPENAI_API_KEY": "Chave da API da OpenAI (opcional)"
    }
    
    all_good = True
    
    for var, description in env_vars.items():
        exists = os.getenv(var) is not None
        print_status(f"{var}", exists, description)
        if var == "GEMINI_API_KEY" and not exists:
            all_good = False
    
    return all_good

def print_installation_guide():
    """Imprime guia de instalação para dependências faltantes."""
    print_header("Guia de Instalação")
    
    print("\n🔧 Para instalar o FFmpeg no Windows:")
    print("   1. Baixe o FFmpeg de: https://ffmpeg.org/download.html")
    print("   2. Extraia o arquivo em C:\\ffmpeg")
    print("   3. Adicione C:\\ffmpeg\\bin ao PATH do sistema")
    print("   4. Reinicie o terminal/PowerShell")
    print("   5. Teste com: ffmpeg -version")
    
    print("\n📦 Para instalar dependências Python:")
    print("   pip install pillow google-genai python-dotenv requests")
    
    print("\n🔑 Para configurar variáveis de ambiente:")
    print("   1. Crie/edite o arquivo .env na raiz do projeto")
    print("   2. Adicione: GEMINI_API_KEY=sua_chave_aqui")
    print("   3. Opcionalmente: OPENAI_API_KEY=sua_chave_openai")

def main():
    """Função principal de verificação."""
    print("🚀 Verificando dependências do AI Video GPT...")
    
    system_ok = check_system_dependencies()
    python_ok = check_python_dependencies()
    env_ok = check_environment_variables()
    
    print_header("Resumo")
    
    if system_ok and python_ok and env_ok:
        print("✅ Todas as dependências estão instaladas!")
        print("🎬 O AI Video GPT está pronto para uso.")
        return True
    else:
        print("❌ Algumas dependências estão faltando.")
        print_installation_guide()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)