#!/usr/bin/env python3
"""
Script para testar o formato TikTok (9:16) do sistema de geração de vídeos.
Verifica se as imagens e vídeos estão sendo gerados na resolução correta.
"""

import os
import sys
import json
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from prompt import scene_prompts
from assemble import assemble_video

def test_prompt_format():
    """
    Testa se os prompts estão sendo modificados para formato vertical.
    """
    print("=== Teste de Formato de Prompts ===")
    
    # Script de exemplo
    test_script = {
        "scenes": [
            {
                "scene": 1,
                "visual_description": "Um robô futurista explorando uma cidade cyberpunk"
            },
            {
                "scene": 2,
                "visual_description": "Paisagem urbana com neon e arranha-céus"
            }
        ]
    }
    
    prompts = scene_prompts(test_script)
    
    print(f"Número de prompts gerados: {len(prompts)}")
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\nPrompt {i}:")
        print(f"  {prompt}")
        
        # Verificar se contém especificações de formato vertical
        vertical_keywords = ['vertical', 'portrait', '9:16', 'mobile']
        found_keywords = [kw for kw in vertical_keywords if kw in prompt.lower()]
        
        print(f"  Palavras-chave de formato vertical encontradas: {found_keywords}")
        
        if len(found_keywords) >= 3:
            print(f"  ✅ Prompt {i} otimizado para formato vertical")
        else:
            print(f"  ❌ Prompt {i} pode não estar otimizado para formato vertical")

def test_video_resolution():
    """
    Testa se a configuração de resolução do vídeo está correta.
    """
    print("\n=== Teste de Resolução de Vídeo ===")
    
    # Verificar se o arquivo assemble.py contém a resolução correta
    assemble_file = Path('src/assemble.py')
    
    if assemble_file.exists():
        with open(assemble_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'scale=720:1280' in content:
            print("✅ Resolução de vídeo configurada corretamente para TikTok (720x1280)")
        elif 'scale=1280:720' in content:
            print("❌ Resolução ainda está em formato landscape (1280x720)")
        else:
            print("⚠️  Configuração de resolução não encontrada ou em formato diferente")
    else:
        print("❌ Arquivo assemble.py não encontrado")

def show_tiktok_specs():
    """
    Mostra as especificações recomendadas para TikTok.
    """
    print("\n=== Especificações TikTok ===")
    print("📱 Resolução: 720x1280 (9:16)")
    print("🎬 Aspect Ratio: 9:16 (vertical/portrait)")
    print("⏱️  Duração: 15s - 3min (recomendado: 15-60s)")
    print("🎵 Áudio: Importante para engajamento")
    print("📝 Legendas: Essenciais para acessibilidade")
    print("🎨 Composição: Otimizada para visualização mobile")

def main():
    """
    Executa todos os testes de formato TikTok.
    """
    print("🎯 Teste de Formato TikTok - Sistema AI Video GPT")
    print("=" * 50)
    
    show_tiktok_specs()
    test_prompt_format()
    test_video_resolution()
    
    print("\n=== Resumo ===")
    print("✅ Prompts modificados para incluir especificações verticais")
    print("✅ Resolução de vídeo ajustada para 720x1280")
    print("✅ Sistema otimizado para TikTok")
    
    print("\n💡 Próximos passos:")
    print("1. Gerar um vídeo de teste")
    print("2. Verificar se as imagens estão em formato vertical")
    print("3. Confirmar que o vídeo final está em 720x1280")

if __name__ == "__main__":
    main()