#!/usr/bin/env python3
"""Script de teste para o sistema de legendas com destaque de palavras-chave.

Este script demonstra como usar o novo sistema de legendas "highlighted subtitle"
que destaca palavras-chave com fundos coloridos, popular em vídeos de redes sociais.
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from core.subtitle import generate_highlighted_subtitles
from core.subtitle_styles import SubtitleStyleManager
from core.subtitle_advanced import ASSGenerator
from utils.keyword_highlighter import KeywordHighlighter

def test_keyword_detection():
    """Testa a detecção automática de palavras-chave."""
    print("\n🔍 Testando detecção de palavras-chave...")
    
    highlighter = KeywordHighlighter()
    
    # Textos de teste
    test_texts = [
        "Let's CREATE something AMAZING today!",
        "BUILD your dreams and make them REAL!",
        "This is IMPORTANT for your SUCCESS!",
        "DISCOVER new opportunities and GROW!",
        "TRANSFORM your life with these POWERFUL tips!"
    ]
    
    for text in test_texts:
        print(f"\n📝 Texto original: {text}")
        
        # Detectar palavras-chave
        keywords = highlighter.detect_keywords(text)
        print(f"🎯 Palavras-chave detectadas: {keywords}")
        
        # Gerar tags ASS
        ass_text = highlighter.generate_ass_tags(text, auto_detect=True)
        print(f"🎨 Texto com tags ASS: {ass_text}")

def test_manual_highlighting():
    """Testa o destaque manual de palavras."""
    print("\n✏️ Testando destaque manual...")
    
    highlighter = KeywordHighlighter()
    
    # Texto com marcações manuais
    text_with_markup = "Welcome to our {SPECIAL:blue} event! Don't miss this {AMAZING:red} opportunity!"
    
    print(f"📝 Texto com marcações: {text_with_markup}")
    
    # Processar marcações
    processed_text = highlighter.parse_manual_markup(text_with_markup)
    print(f"🎨 Texto processado: {processed_text}")
    
    # Gerar tags ASS
    ass_text = highlighter.generate_ass_tags(text_with_markup, auto_detect=False)
    print(f"🎬 Tags ASS: {ass_text}")

def test_ass_generation():
    """Testa a geração de arquivos ASS."""
    print("\n🎬 Testando geração de arquivos ASS...")
    
    # Criar diretório de teste
    test_dir = "test_highlighted_output"
    os.makedirs(test_dir, exist_ok=True)
    
    # Conteúdo SRT de exemplo
    srt_content = """1
00:00:00,000 --> 00:00:03,000
Let's CREATE something AMAZING!

2
00:00:03,500 --> 00:00:06,500
This is a {SPECIAL:blue} moment to celebrate!

3
00:00:07,000 --> 00:00:10,000
BUILD your dreams and make them REAL!

4
00:00:10,500 --> 00:00:13,500
DISCOVER new opportunities and GROW!

5
00:00:14,000 --> 00:00:17,000
TRANSFORM your life with POWERFUL tips!
"""
    
    # Salvar SRT de teste
    srt_file = os.path.join(test_dir, "test_subtitles.srt")
    with open(srt_file, 'w', encoding='utf-8') as f:
        f.write(srt_content)
    
    print(f"📄 Arquivo SRT criado: {srt_file}")
    
    # Obter estilo highlighted
    style = SubtitleStyleManager.get_style("highlighted")
    
    # Criar gerador ASS
    generator = ASSGenerator(1280, 720)  # Formato landscape
    
    # Adicionar destaques personalizados
    generator.add_custom_highlight("TESTE", "#FF0000")  # Vermelho
    generator.add_custom_highlight("DEMO", "#00FF00")   # Verde
    
    # Gerar arquivo ASS
    ass_file = os.path.join(test_dir, "test_highlighted.ass")
    generator.save_ass_file(
        srt_content=srt_content,
        output_path=ass_file,
        style=style,
        highlight_keywords=True,
        auto_detect=True
    )
    
    print(f"🎨 Arquivo ASS gerado: {ass_file}")
    
    # Mostrar filtro FFmpeg
    ffmpeg_filter = generator.get_ffmpeg_filter(ass_file)
    print(f"🎬 Filtro FFmpeg: {ffmpeg_filter}")
    
    # Ler e mostrar parte do conteúdo ASS
    with open(ass_file, 'r', encoding='utf-8') as f:
        ass_content = f.read()
    
    print(f"\n📋 Primeiras linhas do arquivo ASS:")
    lines = ass_content.split('\n')[:20]
    for line in lines:
        print(f"   {line}")
    
    return test_dir, srt_file, ass_file

def test_different_formats():
    """Testa diferentes formatos de vídeo."""
    print("\n📐 Testando diferentes formatos...")
    
    formats = [
        {"name": "TikTok (9:16)", "width": 720, "height": 1280},
        {"name": "YouTube (16:9)", "width": 1920, "height": 1080},
        {"name": "Instagram Square", "width": 1080, "height": 1080},
        {"name": "YouTube Shorts (9:16)", "width": 1080, "height": 1920}
    ]
    
    test_dir = "test_formats_output"
    os.makedirs(test_dir, exist_ok=True)
    
    srt_content = """1
00:00:00,000 --> 00:00:03,000
CREATE amazing content for {SOCIAL:blue} media!

2
00:00:03,500 --> 00:00:06,500
MAKE your videos STAND OUT!
"""
    
    for fmt in formats:
        print(f"\n🎯 Testando formato: {fmt['name']} ({fmt['width']}x{fmt['height']})")
        
        # Criar gerador para este formato
        generator = ASSGenerator(fmt['width'], fmt['height'])
        
        # Obter estilo apropriado
        if fmt['height'] > fmt['width']:  # Formato vertical
            style = SubtitleStyleManager.get_style("tiktok")
        else:
            style = SubtitleStyleManager.get_style("highlighted")
        
        # Gerar arquivo ASS
        ass_file = os.path.join(test_dir, f"test_{fmt['name'].lower().replace(' ', '_')}.ass")
        generator.save_ass_file(
            srt_content=srt_content,
            output_path=ass_file,
            style=style,
            highlight_keywords=True,
            auto_detect=True
        )
        
        print(f"   ✅ Arquivo gerado: {os.path.basename(ass_file)}")
        print(f"   🎬 Filtro FFmpeg: {generator.get_ffmpeg_filter(ass_file)}")

def test_style_variations():
    """Testa variações de estilos."""
    print("\n🎨 Testando variações de estilos...")
    
    styles = ["highlighted", "tiktok", "modern", "pop"]
    
    test_dir = "test_styles_output"
    os.makedirs(test_dir, exist_ok=True)
    
    srt_content = """1
00:00:00,000 --> 00:00:03,000
Testing DIFFERENT styles for HIGHLIGHTED subtitles!
"""
    
    for style_name in styles:
        print(f"\n🎪 Testando estilo: {style_name}")
        
        try:
            style = SubtitleStyleManager.get_style(style_name)
            if not style:
                print(f"   ⚠️ Estilo '{style_name}' não encontrado")
                continue
            
            generator = ASSGenerator(1280, 720)
            
            ass_file = os.path.join(test_dir, f"test_style_{style_name}.ass")
            generator.save_ass_file(
                srt_content=srt_content,
                output_path=ass_file,
                style=style,
                highlight_keywords=True,
                auto_detect=True
            )
            
            print(f"   ✅ Arquivo gerado: {os.path.basename(ass_file)}")
            
        except Exception as e:
            print(f"   ❌ Erro com estilo '{style_name}': {e}")

def show_usage_examples():
    """Mostra exemplos de uso do sistema."""
    print("\n📚 Exemplos de uso do sistema:")
    
    print("\n1️⃣ Uso básico com detecção automática:")
    print("```python")
    print("from core.subtitle import generate_highlighted_subtitles")
    print("")
    print("results = generate_highlighted_subtitles(")
    print("    audio_files=['audio.wav'],")
    print("    output_dir='output',")
    print("    style_name='highlighted',")
    print("    highlight_keywords=True,")
    print("    auto_detect=True")
    print(")")
    print("```")
    
    print("\n2️⃣ Uso com destaques personalizados:")
    print("```python")
    print("results = generate_highlighted_subtitles(")
    print("    audio_files=['audio.wav'],")
    print("    output_dir='output',")
    print("    custom_highlights={")
    print("        'MARCA': '#FF0000',  # Vermelho")
    print("        'PRODUTO': '#0000FF'  # Azul")
    print("    }")
    print(")")
    print("```")
    
    print("\n3️⃣ Uso para TikTok (formato vertical):")
    print("```python")
    print("results = generate_highlighted_subtitles(")
    print("    audio_files=['audio.wav'],")
    print("    output_dir='output',")
    print("    style_name='tiktok',")
    print("    video_width=720,")
    print("    video_height=1280")
    print(")")
    print("```")
    
    print("\n4️⃣ Marcação manual no texto:")
    print("```")
    print("Texto: 'Welcome to our {SPECIAL:blue} event!'")
    print("Resultado: Palavra 'SPECIAL' com fundo azul")
    print("```")
    
    print("\n5️⃣ Aplicar no FFmpeg:")
    print("```bash")
    print("ffmpeg -i video.mp4 -vf \"ass=subtitles_highlighted.ass\" output.mp4")
    print("```")

def main():
    """Função principal de teste."""
    print("🎯 Sistema de Legendas com Destaque de Palavras-chave")
    print("=" * 60)
    
    try:
        # Executar testes
        test_keyword_detection()
        test_manual_highlighting()
        test_dir, srt_file, ass_file = test_ass_generation()
        test_different_formats()
        test_style_variations()
        
        # Mostrar exemplos de uso
        show_usage_examples()
        
        print("\n✅ Todos os testes concluídos com sucesso!")
        print(f"\n📁 Arquivos de teste gerados em:")
        print(f"   - {test_dir}/")
        print(f"   - test_formats_output/")
        print(f"   - test_styles_output/")
        
        print("\n🎬 Para usar as legendas em um vídeo:")
        print(f"   ffmpeg -i video.mp4 -vf \"ass={ass_file}\" output.mp4")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()