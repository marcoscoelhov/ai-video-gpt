"""Exemplo de uso da classe GeminiImagenClient.

Este arquivo demonstra como usar a classe GeminiImagenClient para gerar
imagens com o Google Gemini 2.0 Flash, incluindo exemplos síncronos,
assíncronos e de geração múltipla.
"""

import os
import asyncio
from pathlib import Path
import sys

# Carregar variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv não instalado. Usando variáveis de ambiente do sistema.")

# Adicionar o diretório pai ao path para importar o cliente
sys.path.append(str(Path(__file__).parent.parent))

from config.gemini_imagen_client import GeminiImagenClient, generate_image_quick


def exemplo_basico():
    """Exemplo básico de geração de imagem."""
    print("=== Exemplo Básico ===")
    
    # Verificar se API key está disponível
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Erro: Defina a variável de ambiente GEMINI_API_KEY")
        return
    
    try:
        # Criar cliente
        client = GeminiImagenClient()
        
        # Gerar imagem
        print("Gerando imagem: 'Um gato astronauta dirigindo um buggy lunar'...")
        result = client.generate_image(
            prompt="Um gato astronauta dirigindo um buggy lunar com a Terra ao fundo, estilo realista",
            output_path="outputs/gato_astronauta.png"
        )
        
        print(f"✅ Imagem salva em: {result['saved_path']}")
        if result['text_response']:
            print(f"📝 Resposta de texto: {result['text_response']}")
        
        # Mostrar informações do modelo
        info = client.get_model_info()
        print(f"ℹ️ Modelo usado: {info['model_name']}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


def exemplo_multiplas_imagens():
    """Exemplo de geração de múltiplas imagens."""
    print("\n=== Exemplo Múltiplas Imagens ===")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Erro: Defina a variável de ambiente GEMINI_API_KEY")
        return
    
    try:
        client = GeminiImagenClient()
        
        # Lista de prompts
        prompts = [
            "Um dragão voando sobre uma cidade futurista",
            "Uma floresta mágica com árvores bioluminescentes",
            "Um robô jardineiro cuidando de flores alienígenas"
        ]
        
        print(f"Gerando {len(prompts)} imagens...")
        results = client.generate_multiple_images(
            prompts=prompts,
            output_dir="outputs/multiplas",
            filename_prefix="fantasia",
            include_text_responses=True
        )
        
        # Mostrar resultados
        for i, result in enumerate(results):
            if 'error' in result:
                print(f"❌ Imagem {i+1}: Erro - {result['error']}")
            else:
                print(f"✅ Imagem {i+1}: {result['saved_path']}")
                if result['text_response']:
                    print(f"   📝 Texto: {result['text_response'][:100]}...")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


async def exemplo_assincrono():
    """Exemplo de geração assíncrona de imagens."""
    print("\n=== Exemplo Assíncrono ===")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Erro: Defina a variável de ambiente GEMINI_API_KEY")
        return
    
    try:
        client = GeminiImagenClient()
        
        # Lista de prompts para geração assíncrona
        prompts = [
            "Uma nave espacial explorando um planeta desconhecido",
            "Um castelo flutuante nas nuvens",
            "Uma cidade subaquática com peixes coloridos"
        ]
        
        print(f"Gerando {len(prompts)} imagens assincronamente...")
        
        # Gerar múltiplas imagens assincronamente
        results = await client.generate_multiple_images_async(
            prompts=prompts,
            output_dir="outputs/async",
            filename_prefix="async_image",
            include_text_responses=True,
            max_concurrent=2  # Máximo 2 requisições simultâneas
        )
        
        # Mostrar resultados
        for i, result in enumerate(results):
            if 'error' in result:
                print(f"❌ Imagem {i+1}: Erro - {result['error']}")
            else:
                print(f"✅ Imagem {i+1}: {result['saved_path']}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


def exemplo_edicao_imagem():
    """Exemplo de edição de imagem existente."""
    print("\n=== Exemplo Edição de Imagem ===")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Erro: Defina a variável de ambiente GEMINI_API_KEY")
        return
    
    try:
        client = GeminiImagenClient()
        
        # Primeiro, verificar se existe uma imagem para editar
        image_path = "outputs/gato_astronauta.png"
        if not Path(image_path).exists():
            print(f"⚠️ Imagem não encontrada: {image_path}")
            print("Execute primeiro o exemplo básico para criar uma imagem.")
            return
        
        print(f"Editando imagem: {image_path}")
        result = client.edit_image(
            image_path=image_path,
            edit_prompt="Adicione um capacete espacial dourado no gato e faça o buggy ser vermelho",
            output_path="outputs/gato_astronauta_editado.png"
        )
        
        print(f"✅ Imagem editada salva em: {result['saved_path']}")
        if result['text_response']:
            print(f"📝 Resposta de texto: {result['text_response']}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


def exemplo_funcao_rapida():
    """Exemplo usando a função de conveniência."""
    print("\n=== Exemplo Função Rápida ===")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Erro: Defina a variável de ambiente GEMINI_API_KEY")
        return
    
    try:
        print("Gerando imagem com função rápida...")
        saved_path = generate_image_quick(
            prompt="Um pôr do sol em Marte com duas luas no céu",
            output_path="outputs/marte_por_do_sol.png"
        )
        
        print(f"✅ Imagem salva em: {saved_path}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


def criar_diretorios():
    """Cria os diretórios necessários para os exemplos."""
    directories = [
        "outputs",
        "outputs/multiplas",
        "outputs/async"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def main():
    """Função principal que executa todos os exemplos."""
    print("🚀 Exemplos de uso do GeminiImagenClient")
    print("========================================")
    
    # Verificar se API key está disponível
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Erro: Variável de ambiente GEMINI_API_KEY não definida.")
        print("")
        print("Para usar este exemplo, defina sua API key:")
        print("Windows: set GEMINI_API_KEY=sua_api_key_aqui")
        print("Linux/Mac: export GEMINI_API_KEY=sua_api_key_aqui")
        print("")
        print("Obtenha sua API key em: https://aistudio.google.com/app/apikey")
        return
    
    # Criar diretórios necessários
    criar_diretorios()
    
    # Executar exemplos
    exemplo_basico()
    exemplo_funcao_rapida()
    exemplo_multiplas_imagens()
    
    # Exemplo assíncrono
    print("\n⏳ Executando exemplo assíncrono...")
    asyncio.run(exemplo_assincrono())
    
    # Exemplo de edição (depende do exemplo básico)
    exemplo_edicao_imagem()
    
    print("\n🎉 Todos os exemplos foram executados!")
    print("Verifique a pasta 'outputs' para ver as imagens geradas.")


if __name__ == "__main__":
    main()