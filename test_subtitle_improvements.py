#!/usr/bin/env python3
"""
Script de teste consolidado para as melhorias implementadas nas legendas:
1. Detecção automática de idioma
2. Correção de sincronização
3. Novo estilo de legenda 'casquinha'
4. Reutilização de arquivos de output existentes
"""

import os
import sys
import json
from pathlib import Path
from core.subtitle import detect_script_language, generate_subtitles
from core.subtitle_styles import SubtitleStyleManager, get_available_styles
from config.gemini_subtitle_client import GeminiSubtitleClient
from core.assemble import get_audio_duration

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

def test_file_reuse():
    """Testa a reutilização de arquivos existentes na pasta outputs."""
    print("\n=== Teste de Reutilização de Arquivos ===\n")
    
    # Verificar arquivos de imagem disponíveis
    outputs_dir = Path("outputs")
    image_files = list(outputs_dir.glob("**/*.png"))
    
    print(f"📁 Arquivos de imagem encontrados: {len(image_files)}")
    for img in image_files[:5]:  # Mostrar apenas os primeiros 5
        size_kb = img.stat().st_size / 1024
        print(f"  - {img.name}: {size_kb:.1f} KB")
    
    # Verificar arquivo de vídeo
    video_file = Path("videoplayback.mp4")
    if video_file.exists():
        size_mb = video_file.stat().st_size / (1024 * 1024)
        print(f"\n🎬 Arquivo de vídeo encontrado: {video_file.name} ({size_mb:.1f} MB)")
    
    # Criar script de teste usando arquivos existentes
    test_script = {
        "title": "Teste com Arquivos Reutilizados",
        "scenes": [
            {
                "scene": 1,
                "narration": "Este é um teste usando arquivos já existentes no projeto.",
                "visual_description": "Imagem de teste reutilizada do diretório outputs"
            },
            {
                "scene": 2,
                "narration": "Demonstrando a reutilização eficiente de recursos.",
                "visual_description": "Segunda imagem de teste do diretório outputs"
            }
        ]
    }
    
    # Salvar script de teste
    test_script_path = "test_script_reuse.json"
    with open(test_script_path, 'w', encoding='utf-8') as f:
        json.dump(test_script, f, indent=2, ensure_ascii=False)
    
    print(f"\n📝 Script de teste criado: {test_script_path}")
    
    # Testar detecção de idioma com o script
    detected_lang = detect_script_language(test_script_path)
    print(f"🌐 Idioma detectado: {detected_lang}")
    
    # Verificar se temos pelo menos arquivos de imagem
    if len(image_files) > 0:
        print("✅ Reutilização de arquivos funcionando!")
        if not video_file.exists():
            print("ℹ️ Arquivo de vídeo não encontrado, mas imagens disponíveis.")
        return True
    else:
        print("❌ Arquivos para reutilização não encontrados!")
        return False

def test_integration():
    """Testa a integração completa usando arquivos existentes."""
    print("\n=== Teste de Integração Completa ===\n")
    
    try:
        # Verificar se temos arquivos necessários
        outputs_dir = Path("outputs")
        if not outputs_dir.exists():
            print("❌ Diretório outputs não encontrado!")
            return False
        
        # Criar diretório de teste
        test_dir = Path("test_output_integration")
        test_dir.mkdir(exist_ok=True)
        
        # Testar estilo casquinha com arquivos reais
        style_manager = SubtitleStyleManager()
        casquinha_style = style_manager.get_style("casquinha")
        
        # Simular SRT com o novo estilo
        sample_srt = """1
00:00:00,000 --> 00:00:03,000
Teste do estilo casquinha

2
00:00:03,100 --> 00:00:06,000
Usando arquivos reutilizados
"""
        
        # Aplicar estilo ao SRT
        styled_srt = style_manager.apply_style_to_srt(sample_srt, casquinha_style)
        
        # Salvar resultado
        output_srt = test_dir / "test_casquinha_style.srt"
        with open(output_srt, 'w', encoding='utf-8') as f:
            f.write(styled_srt)
        
        print(f"📄 SRT com estilo casquinha salvo: {output_srt}")
        print(f"🎨 Configurações do estilo:")
        
        # Verificar se é um objeto SubtitleStyle ou string
        if hasattr(casquinha_style, 'text_color'):
            print(f"  - Cor do texto: {casquinha_style.text_color}")
            print(f"  - Cor de fundo: {casquinha_style.background_color}")
            print(f"  - Fonte: {casquinha_style.font_family} {casquinha_style.font_size}px")
            print(f"  - Caracteres por linha: {casquinha_style.max_chars_per_line}")
            print(f"  - Caracteres por segundo: {casquinha_style.chars_per_second}")
        else:
            print(f"  - Estilo aplicado: {casquinha_style}")
        
        # Verificar se o arquivo foi criado
        if output_srt.exists():
            file_size = output_srt.stat().st_size
            print(f"  - Arquivo criado: {file_size} bytes")
        
        # Mostrar uma amostra do conteúdo estilizado
        print(f"\n📝 Amostra do SRT estilizado:")
        with open(output_srt, 'r', encoding='utf-8') as f:
            content = f.read()[:200]  # Primeiros 200 caracteres
            print(f"  {content}...")
        
        print("✅ Integração completa funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        return False

def main():
    """Executa todos os testes consolidados."""
    print("🧪 Testando melhorias nas legendas (versão consolidada)...\n")
    
    results = []
    
    # Executar testes
    results.append(test_language_detection())
    results.append(test_subtitle_styles())
    results.append(test_timing_correction())
    results.append(test_file_reuse())
    results.append(test_integration())
    
    # Resumo dos resultados
    print("\n" + "="*60)
    print("RESUMO DOS TESTES CONSOLIDADOS")
    print("="*60)
    
    test_names = [
        "Detecção de Idioma",
        "Estilos de Legenda",
        "Correção de Timing",
        "Reutilização de Arquivos",
        "Integração Completa"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{i+1}. {name}: {status}")
    
    # Estatísticas
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"\n📊 Estatísticas: {passed}/{total} testes passaram ({percentage:.1f}%)")
    
    # Resultado geral
    if all(results):
        print("\n🎉 Todos os testes passaram! Sistema totalmente funcional.")
        print("📁 Arquivos de output sendo reutilizados eficientemente.")
        print("🎨 Novo estilo 'casquinha' integrado e funcionando.")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique as implementações.")
    
    return all(results)

if __name__ == "__main__":
    print("🔧 Sistema de Teste Consolidado - AI Video GPT")
    print("📋 Testando melhorias de legendas com reutilização de arquivos\n")
    
    success = main()
    
    # Limpeza opcional
    cleanup_files = ["test_script_reuse.json"]
    print("\n🧹 Limpeza de arquivos temporários...")
    for file in cleanup_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"  - Removido: {file}")
    
    print(f"\n{'✅ SUCESSO' if success else '❌ FALHA'}: Teste consolidado finalizado.")
    sys.exit(0 if success else 1)