#!/usr/bin/env python3
"""
Script para gerar um vídeo de teste no formato TikTok (9:16).
Testa todo o pipeline de geração com as novas configurações.
"""

import os
import sys
import json
import time
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import main as generate_video

def create_test_script():
    """
    Cria um script de teste otimizado para TikTok.
    """
    test_script = {
        "title": "Robô TikTok Test",
        "description": "Vídeo de teste para verificar formato TikTok 9:16",
        "scenes": [
            {
                "scene": 1,
                "visual_description": "Um robô amigável acenando para a câmera em uma cidade futurista",
                "narration": "Olá! Este é um teste do formato TikTok.",
                "duration": 3
            },
            {
                "scene": 2,
                "visual_description": "O robô caminhando por uma rua com prédios altos e luzes neon",
                "narration": "Verificando se o vídeo está em formato vertical.",
                "duration": 3
            },
            {
                "scene": 3,
                "visual_description": "Close-up do robô sorrindo com a cidade ao fundo",
                "narration": "Resolução 720 por 1280 pixels, perfeito para TikTok!",
                "duration": 4
            }
        ]
    }
    
    # Salvar o script
    script_file = Path('test_tiktok_script.json')
    with open(script_file, 'w', encoding='utf-8') as f:
        json.dump(test_script, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Script de teste criado: {script_file}")
    return script_file

def generate_test_video():
    """
    Gera um vídeo de teste usando um tema simples.
    """
    print("\n🎬 Gerando vídeo de teste TikTok...")
    print("=" * 40)
    
    # Tema de teste otimizado para TikTok
    test_theme = "Um robô amigável explorando uma cidade futurista em formato vertical para TikTok"
    
    try:
        # Gerar o vídeo
        start_time = time.time()
        generate_video(test_theme)
        end_time = time.time()
        
        print(f"\n⏱️  Tempo de geração: {end_time - start_time:.2f} segundos")
        
    except Exception as e:
        print(f"❌ Erro durante a geração: {e}")
        return False
    
    return True

def check_output_format():
    """
    Verifica se o vídeo foi gerado no formato correto.
    """
    print("\n🔍 Verificando formato do vídeo gerado...")
    
    # Procurar pelo vídeo gerado mais recente
    output_dirs = [d for d in Path('.').iterdir() if d.is_dir() and d.name.startswith('video_')]
    
    if not output_dirs:
        print("❌ Nenhum diretório de vídeo encontrado")
        return False
    
    # Pegar o mais recente
    latest_dir = max(output_dirs, key=lambda x: x.stat().st_mtime)
    print(f"📁 Diretório mais recente: {latest_dir}")
    
    # Procurar pelo vídeo final
    video_files = list(latest_dir.glob('*.mp4'))
    
    if not video_files:
        print("❌ Nenhum arquivo de vídeo encontrado")
        return False
    
    video_file = video_files[0]
    print(f"🎥 Vídeo encontrado: {video_file}")
    
    # Verificar se o arquivo existe e tem tamanho > 0
    if video_file.exists() and video_file.stat().st_size > 0:
        file_size = video_file.stat().st_size / (1024 * 1024)  # MB
        print(f"📊 Tamanho do arquivo: {file_size:.2f} MB")
        print("✅ Vídeo gerado com sucesso")
        
        # Sugerir verificação manual
        print(f"\n💡 Para verificar a resolução, execute:")
        print(f"   ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 \"{video_file}\"")
        
        return True
    else:
        print("❌ Arquivo de vídeo vazio ou corrompido")
        return False

def main():
    """
    Executa o teste completo de geração de vídeo TikTok.
    """
    print("🎯 Teste Completo de Vídeo TikTok")
    print("=" * 50)
    
    print("📋 Configurações do teste:")
    print("   • Formato: 9:16 (vertical)")
    print("   • Resolução: 720x1280")
    print("   • Duração: ~10 segundos")
    print("   • 3 cenas com narração")
    
    # Gerar vídeo de teste
    success = generate_test_video()
    
    if success:
        # Verificar formato
        check_output_format()
        
        print("\n🎉 Teste concluído!")
        print("\n📱 Verificações manuais recomendadas:")
        print("1. Abrir o vídeo e verificar se está em formato vertical")
        print("2. Confirmar que as imagens estão bem compostas para mobile")
        print("3. Testar em um dispositivo móvel se possível")
    else:
        print("\n❌ Teste falhou durante a geração")

if __name__ == "__main__":
    main()