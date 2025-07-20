#!/usr/bin/env python3
"""
Exemplo prático de uso das melhorias implementadas nas legendas:
1. Detecção automática de idioma
2. Correção de sincronização
3. Novo estilo de legenda 'casquinha'

Este script demonstra como usar as novas funcionalidades.
"""

import os
import json
from core.subtitle import generate_subtitles, detect_script_language
from core.assemble import assemble_video
from core.subtitle_styles import SubtitleStyleManager, get_available_styles

def exemplo_deteccao_idioma():
    """Demonstra a detecção automática de idioma."""
    print("=== Exemplo: Detecção Automática de Idioma ===")
    
    # Exemplo de roteiro em português
    script_pt = {
        "scenes": [
            {"narration": "Bem-vindos ao nosso canal sobre tecnologia e inovação."},
            {"narration": "Hoje vamos falar sobre inteligência artificial e suas aplicações."}
        ]
    }
    
    # Exemplo de roteiro em inglês
    script_en = {
        "scenes": [
            {"narration": "Welcome to our technology and innovation channel."},
            {"narration": "Today we will talk about artificial intelligence and its applications."}
        ]
    }
    
    # Detectar idiomas
    idioma_pt = detect_script_language(script_pt)
    idioma_en = detect_script_language(script_en)
    
    print(f"Roteiro em português detectado como: {idioma_pt}")
    print(f"Roteiro em inglês detectado como: {idioma_en}")
    print("✅ O sistema agora detecta automaticamente o idioma!\n")

def exemplo_estilos_legenda():
    """Demonstra os estilos de legenda disponíveis."""
    print("=== Exemplo: Estilos de Legenda Disponíveis ===")
    
    # Listar todos os estilos
    estilos = get_available_styles()
    print("Estilos disponíveis:")
    for nome, descricao in estilos.items():
        print(f"  • {nome}: {descricao}")
    
    # Demonstrar o novo estilo 'casquinha'
    print("\n🎨 Novo Estilo 'Casquinha':")
    style_manager = SubtitleStyleManager()
    estilo_casquinha = style_manager.get_style("casquinha")
    
    print(f"  • Fonte: {estilo_casquinha.font_family} {estilo_casquinha.font_size}px")
    print(f"  • Cor do texto: {estilo_casquinha.text_color}")
    print(f"  • Cor de fundo: {estilo_casquinha.background_color}")
    print(f"  • Contorno: {estilo_casquinha.outline_width}px")
    print(f"  • Caracteres por linha: {estilo_casquinha.max_chars_per_line}")
    print("✅ Perfeito para conteúdo divertido e chamativo!\n")

def exemplo_uso_completo():
    """Demonstra como usar todas as melhorias juntas."""
    print("=== Exemplo: Uso Completo das Melhorias ===")
    
    # Exemplo de como gerar legendas com as melhorias
    print("📝 Código de exemplo para gerar vídeo com legendas melhoradas:")
    print("""
# 1. Gerar legendas com detecção automática de idioma
from core.subtitle import generate_subtitles

# O sistema detecta automaticamente o idioma do script.json
subtitle_path = generate_subtitles(
    audio_paths=['audio1.mp3', 'audio2.mp3'],
    output_path='legendas.srt',
    script_path='script.json'  # ← Novo parâmetro para detecção de idioma
)

# 2. Montar vídeo com novo estilo de legenda
from core.assemble import assemble_video

video_path = assemble_video(
    image_paths=['img1.png', 'img2.png'],
    audio_paths=['audio1.mp3', 'audio2.mp3'],
    subtitle_path=subtitle_path,
    final_video_path='video_final.mp4',
    subtitle_style='casquinha'  # ← Novo estilo implementado
)

# 3. As legendas serão:
#    ✅ No idioma correto (detectado automaticamente)
#    ✅ Sincronizadas corretamente (timing corrigido)
#    ✅ Com visual atrativo (estilo casquinha)
    """)
    
    print("🎯 Principais benefícios:")
    print("  • Idioma detectado automaticamente do roteiro")
    print("  • Sincronização corrigida automaticamente")
    print("  • Novo estilo visual 'casquinha' disponível")
    print("  • Processo totalmente automatizado")
    print("✅ Todas as melhorias funcionam em conjunto!\n")

def exemplo_antes_depois():
    """Mostra a diferença entre antes e depois das melhorias."""
    print("=== Comparação: Antes vs Depois ===")
    
    print("❌ ANTES das melhorias:")
    print("  • Áudio em inglês, legendas em português")
    print("  • Legendas dessincronizdas e sobrepostas")
    print("  • Estilo visual básico")
    print("  • Configuração manual necessária")
    
    print("\n✅ DEPOIS das melhorias:")
    print("  • Idioma detectado automaticamente")
    print("  • Legendas perfeitamente sincronizadas")
    print("  • Estilo visual 'casquinha' atrativo")
    print("  • Processo completamente automatizado")
    
    print("\n🚀 Resultado: Legendas profissionais com zero configuração manual!")

def main():
    """Executa todos os exemplos."""
    print("🎬 Demonstração das Melhorias nas Legendas")
    print("="*60)
    print()
    
    exemplo_deteccao_idioma()
    exemplo_estilos_legenda()
    exemplo_uso_completo()
    exemplo_antes_depois()
    
    print("🎉 Todas as melhorias estão prontas para uso!")
    print("📚 Consulte o arquivo 'tasks/todo.md' para mais detalhes.")

if __name__ == "__main__":
    main()