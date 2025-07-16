#!/usr/bin/env python3
"""
Script para gerar vídeos otimizados para TikTok (formato 9:16)

Este script utiliza o sistema AI Video GPT otimizado para gerar vídeos
no formato vertical ideal para TikTok e outras plataformas de vídeo mobile.

Características:
- Resolução: 720x1280 (9:16)
- Prompts otimizados para composição vertical
- Geração automática de legendas
- Montagem com FFmpeg

Uso:
    python generate_tiktok_video.py "Seu tema aqui"

Exemplos:
    python generate_tiktok_video.py "Um gato ninja explorando Tóquio"
    python generate_tiktok_video.py "Receita de bolo de chocolate em 30 segundos"
    python generate_tiktok_video.py "Tutorial de dança futurista"
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from main import main

def generate_tiktok_video(theme):
    """
    Gera um vídeo otimizado para TikTok com o tema fornecido.
    
    Args:
        theme (str): O tema ou descrição do vídeo a ser gerado
        
    Returns:
        str: Caminho para o vídeo gerado ou None se falhou
    """
    print("🎯 Gerador de Vídeos TikTok - AI Video GPT")
    print("=" * 50)
    print(f"📱 Tema: {theme}")
    print("📐 Formato: 9:16 (720x1280)")
    print("🎨 Otimizado para visualização mobile")
    print("📝 Com legendas automáticas")
    print("=" * 50)
    
    # Verificar se as chaves de API estão configuradas
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Erro: GEMINI_API_KEY não configurada")
        print("   Configure sua chave de API no arquivo .env")
        return None
    
    try:
        # Gerar o vídeo
        main(theme)
        
        # Verificar se o vídeo foi criado
        video_path = "output/final_video.mp4"
        if os.path.exists(video_path):
            print("\n🎉 Vídeo TikTok gerado com sucesso!")
            print(f"📁 Localização: {os.path.abspath(video_path)}")
            print("\n📱 Próximos passos:")
            print("   1. Abra o vídeo para verificar a qualidade")
            print("   2. Teste em um dispositivo móvel")
            print("   3. Faça upload para TikTok, Instagram Reels, etc.")
            return video_path
        else:
            print("\n❌ Erro: Vídeo não foi gerado")
            return None
            
    except Exception as e:
        print(f"\n❌ Erro durante a geração: {e}")
        return None

def main_cli():
    """
    Interface de linha de comando para o gerador de vídeos TikTok.
    """
    if len(sys.argv) != 2:
        print("Uso: python generate_tiktok_video.py \"Seu tema aqui\"")
        print("\nExemplos:")
        print('  python generate_tiktok_video.py "Um robô explorando uma cidade futurista"')
        print('  python generate_tiktok_video.py "Receita rápida de smoothie"')
        print('  python generate_tiktok_video.py "Dicas de produtividade para estudantes"')
        sys.exit(1)
    
    theme = sys.argv[1]
    
    # Adicionar contexto para TikTok se não estiver presente
    if "tiktok" not in theme.lower() and "vertical" not in theme.lower():
        theme += " em formato vertical para TikTok"
    
    generate_tiktok_video(theme)

if __name__ == "__main__":
    main_cli()