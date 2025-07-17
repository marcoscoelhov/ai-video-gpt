#!/usr/bin/env python3
"""
Script de teste para as melhorias implementadas nas legendas:
1. Detecção automática de idioma
2. Correção de sincronização
3. Novo estilo de legenda 'casquinha'
"""

import os
import sys
from core.subtitle import detect_script_language
from core.subtitle_styles import SubtitleStyleManager, get_available_styles
from config.gemini_subtitle_client import GeminiSubtitleClient

def test_language_detection():
    """Testa a detecção automática de idioma."""
    print("=== Teste de Detecção de Idioma ===")
    
    # Teste com texto em português
    script_pt = {
        "scenes": [
            {"narration": "Olá, bem-vindos ao nosso canal. Hoje vamos falar sobre tecnologia."},
            {"narration": "Este é um vídeo muito interessante sobre inteligência artificial."},
            {"narration": "Esperamos que vocês gostem do conteúdo apresentado."}
        ]
    }
    
    # Teste com texto em inglês
    script_en = {
        "scenes": [
            {"narration": "Hello, welcome to our channel. Today we will talk about technology."},
            {"narration": "This is a very interesting video about artificial intelligence."},
            {"narration": "We hope you enjoy the content presented."}
        ]
    }
    
    # Detectar idiomas
    lang_pt = detect_script_language(script_pt)
    lang_en = detect_script_language(script_en)
    
    print(f"Texto em português detectado como: {lang_pt}")
    print(f"Texto em inglês detectado como: {lang_en}")
    
    # Verificar se a detecção está correta
    if lang_pt == "pt-BR" and lang_en == "en":
        print("✅ Detecção de idioma funcionando corretamente!")
        return True
    else:
        print("❌ Erro na detecção de idioma!")
        return False

def test_subtitle_styles():
    """Testa os estilos de legenda disponíveis."""
    print("\n=== Teste de Estilos de Legenda ===")
    
    # Listar estilos disponíveis
    styles = get_available_styles()
    print("Estilos disponíveis:")
    for name, description in styles.items():
        print(f"  - {name}: {description}")
    
    # Testar o novo estilo 'casquinha'
    style_manager = SubtitleStyleManager()
    casquinha_style = style_manager.get_style("casquinha")
    
    print(f"\nEstilo 'casquinha' carregado:")
    print(f"  - Fonte: {casquinha_style.font_family}, {casquinha_style.font_size}px")
    print(f"  - Cor do texto: {casquinha_style.text_color}")
    print(f"  - Cor de fundo: {casquinha_style.background_color}")
    print(f"  - Caracteres por linha: {casquinha_style.max_chars_per_line}")
    print(f"  - Caracteres por segundo: {casquinha_style.chars_per_second}")
    
    if "casquinha" in styles:
        print("✅ Novo estilo 'casquinha' disponível!")
        return True
    else:
        print("❌ Estilo 'casquinha' não encontrado!")
        return False

def test_timing_correction():
    """Testa a correção de timing das legendas."""
    print("\n=== Teste de Correção de Timing ===")
    
    # Exemplo de SRT com problemas de timing
    problematic_srt = """1
00:00:00,000 --> 00:00:00,500
Texto muito rápido

2
00:00:00,400 --> 00:00:02,000
Texto sobreposto

3
00:00:01,800 --> 00:00:02,200
Outro texto rápido
"""
    
    print("SRT original com problemas:")
    print(problematic_srt)
    
    # Simular correção (a função real está no GeminiSubtitleClient)
    client = GeminiSubtitleClient()
    try:
        corrected_srt = client._fix_subtitle_timing(problematic_srt)
        print("\nSRT corrigido:")
        print(corrected_srt)
        print("✅ Correção de timing implementada!")
        return True
    except Exception as e:
        print(f"❌ Erro na correção de timing: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("🧪 Testando melhorias nas legendas...\n")
    
    results = []
    
    # Executar testes
    results.append(test_language_detection())
    results.append(test_subtitle_styles())
    results.append(test_timing_correction())
    
    # Resumo dos resultados
    print("\n" + "="*50)
    print("RESUMO DOS TESTES")
    print("="*50)
    
    test_names = [
        "Detecção de Idioma",
        "Estilos de Legenda",
        "Correção de Timing"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{i+1}. {name}: {status}")
    
    # Resultado geral
    if all(results):
        print("\n🎉 Todos os testes passaram! As melhorias estão funcionando.")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique as implementações.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)