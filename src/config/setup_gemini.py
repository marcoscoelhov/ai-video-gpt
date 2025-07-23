#!/usr/bin/env python3
"""Script de configuração para a integração com Google Gemini 2.0 Flash.

Este script automatiza a instalação e configuração necessária para usar
a geração de imagens com Google Gemini 2.0 Flash.
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header():
    """Imprime cabeçalho do script."""
    print("="*60)
    print("🚀 Configuração Google Gemini 2.0 Flash - AI Video GPT")
    print("="*60)
    print()


def check_python_version():
    """Verifica se a versão do Python é compatível."""
    print("📋 Verificando versão do Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Erro: Python 3.8+ é necessário")
        print(f"   Versão atual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - OK")
    return True


def install_dependencies():
    """Instala as dependências necessárias."""
    print("\n📦 Instalando dependências...")
    
    try:
        # Verificar se requirements.txt existe
        requirements_file = Path("requirements.txt")
        if not requirements_file.exists():
            print("❌ Arquivo requirements.txt não encontrado")
            return False
        
        # Instalar dependências
        print("   Executando: pip install -r requirements.txt")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True,
            shell=False,  # Never use shell
            timeout=300   # 5 minute timeout
        )
        
        if result.returncode != 0:
            print(f"❌ Erro na instalação: {result.stderr}")
            return False
        
        print("✅ Dependências instaladas com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False


def check_dependencies():
    """Verifica se as dependências estão instaladas."""
    print("\n🔍 Verificando dependências...")
    
    dependencies = [
        ("google.genai", "google-genai"),
        ("PIL", "Pillow"),
        ("requests", "requests")
    ]
    
    missing = []
    
    for module, package in dependencies:
        try:
            __import__(module)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Não encontrado")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️ Dependências faltando: {', '.join(missing)}")
        return False
    
    return True


def setup_api_key():
    """Configura a API key do Gemini."""
    print("\n🔑 Configuração da API Key...")
    
    # Verificar se já existe
    existing_key = os.getenv('GEMINI_API_KEY')
    if existing_key:
        print("✅ GEMINI_API_KEY já está definida")
        return True
    
    print("\n📝 A API key do Google Gemini não foi encontrada.")
    print("\nPara obter sua API key:")
    print("1. Acesse: https://aistudio.google.com/app/apikey")
    print("2. Faça login com sua conta Google")
    print("3. Clique em 'Create API Key'")
    print("4. Copie a API key gerada")
    
    while True:
        print("\nEscolha uma opção:")
        print("1. Inserir API key agora")
        print("2. Configurar depois manualmente")
        print("3. Pular configuração")
        
        choice = input("\nOpção (1-3): ").strip()
        
        if choice == "1":
            api_key = input("\nCole sua API key aqui: ").strip()
            if api_key:
                return create_env_file(api_key)
            else:
                print("❌ API key não pode estar vazia")
        
        elif choice == "2":
            print("\n📋 Para configurar manualmente:")
            print("\nWindows:")
            print("   set GEMINI_API_KEY=sua_api_key_aqui")
            print("\nLinux/Mac:")
            print("   export GEMINI_API_KEY=sua_api_key_aqui")
            print("\nOu crie um arquivo .env com:")
            print("   GEMINI_API_KEY=sua_api_key_aqui")
            return True
        
        elif choice == "3":
            print("⚠️ Configuração da API key pulada")
            return True
        
        else:
            print("❌ Opção inválida")


def create_env_file(api_key):
    """Cria arquivo .env com a API key."""
    try:
        env_file = Path(".env")
        
        # Ler conteúdo existente se arquivo existe
        existing_content = ""
        if env_file.exists():
            existing_content = env_file.read_text()
        
        # Verificar se GEMINI_API_KEY já existe no arquivo
        lines = existing_content.split('\n')
        updated_lines = []
        key_found = False
        
        for line in lines:
            if line.startswith('GEMINI_API_KEY='):
                updated_lines.append(f'GEMINI_API_KEY={api_key}')
                key_found = True
            else:
                updated_lines.append(line)
        
        # Se não encontrou, adicionar no final
        if not key_found:
            if existing_content and not existing_content.endswith('\n'):
                updated_lines.append('')
            updated_lines.append(f'GEMINI_API_KEY={api_key}')
        
        # Escrever arquivo
        env_file.write_text('\n'.join(updated_lines))
        
        print(f"✅ API key salva em {env_file.absolute()}")
        print("\n⚠️ IMPORTANTE: Não compartilhe este arquivo .env")
        print("   Adicione .env ao seu .gitignore se usar Git")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo .env: {e}")
        return False


def test_installation():
    """Testa a instalação básica."""
    print("\n🧪 Testando instalação...")
    
    try:
        # Importar cliente
        from gemini_imagen_client import GeminiImagenClient
        print("✅ Importação do GeminiImagenClient - OK")
        
        # Verificar se pode inicializar (sem fazer requisições)
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            try:
                client = GeminiImagenClient(api_key=api_key)
                info = client.get_model_info()
                print(f"✅ Cliente inicializado - Modelo: {info['model_name']}")
            except Exception as e:
                print(f"⚠️ Cliente inicializado mas pode haver problemas: {e}")
        else:
            print("⚠️ API key não configurada - teste limitado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False


def show_next_steps():
    """Mostra próximos passos após instalação."""
    print("\n🎉 Configuração concluída!")
    print("\n📚 Próximos passos:")
    print("\n1. Testar a instalação:")
    print("   python examples/gemini_imagen_example.py")
    print("\n2. Executar testes:")
    print("   python test_gemini_imagen.py")
    print("\n3. Ler a documentação:")
    print("   Abra GEMINI_IMAGEN_README.md")
    print("\n4. Usar em seu código:")
    print("   from gemini_imagen_client import GeminiImagenClient")
    print("   client = GeminiImagenClient()")
    print("   result = client.generate_image('Seu prompt aqui')")
    
    print("\n📖 Documentação completa: GEMINI_IMAGEN_README.md")
    print("🐛 Problemas? Verifique o arquivo de tarefas: tasks/todo.md")


def main():
    """Função principal do script de configuração."""
    print_header()
    
    # Verificações e instalação
    steps = [
        ("Verificar Python", check_python_version),
        ("Instalar dependências", install_dependencies),
        ("Verificar dependências", check_dependencies),
        ("Configurar API key", setup_api_key),
        ("Testar instalação", test_installation)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"\n❌ Falha em: {step_name}")
            print("\n🛠️ Resolva os problemas acima e execute novamente.")
            return False
    
    show_next_steps()
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Configuração cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        sys.exit(1)