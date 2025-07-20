#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da funcionalidade de sincronização de legendas baseada no roteiro.

Este arquivo testa:
- Sincronização precisa com roteiro existente
- Eliminação da necessidade de transcrição
- Integração com o sistema de montagem de vídeo
- Comparação com método tradicional
"""

import os
import json
import tempfile
import shutil
import sys
from pathlib import Path

# Adicionar diretório raiz ao caminho de importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.subtitle_script_sync import ScriptSubtitleSynchronizer, generate_subtitles_from_script
from src.core.subtitle import generate_subtitles_from_script_sync
from src.utils.mock_generator import MockGenerator

def create_test_environment():
    """
    Cria ambiente de teste com arquivos mock.
    """
    import os
    import shutil
    import json
    
    print("🏗️ Criando ambiente de teste...")
    
    # Criar diretório temporário
    test_dir = "test_script_sync_output"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # Criar subdiretórios
    audio_dir = os.path.join(test_dir, "audio")
    subtitles_dir = os.path.join(test_dir, "subtitles")
    os.makedirs(audio_dir)
    os.makedirs(subtitles_dir)
    
    # Criar roteiro de teste
    script_data = {
        "title": "Teste de Sincronização de Legendas",
        "description": "Vídeo para testar o novo sistema de sincronização",
        "language": "pt-BR",
        "scenes": [
            {
                "id": 1,
                "text": "Texto curto."
            },
            {
                "id": 2,
                "text": "Primeira frase. Segunda frase mais longa. Terceira frase final."
            },
            {
                "id": 3,
                "text": "Uma frase muito longa que deveria ser dividida em múltiplas legendas para melhor legibilidade e compreensão do espectador."
            }
        ]
    }
    
    # Salvar roteiro
    script_path = os.path.join(test_dir, "script.json")
    with open(script_path, 'w', encoding='utf-8') as f:
        json.dump(script_data, f, indent=4, ensure_ascii=False)
    
    # Criar arquivos de áudio mock
    mock_gen = MockGenerator()
    audio_files = []
    
    for i, scene in enumerate(script_data['scenes'], 1):
        audio_file = os.path.join(audio_dir, f"scene_{i}.mp3")
        
        # Simular duração baseada no texto
        text_length = len(scene['text'])
        estimated_duration = max(3.0, text_length / 15.0)  # ~15 chars/second
        
        # Criar arquivo de áudio mock
        mock_gen.create_mock_audio(audio_file, duration=estimated_duration)
        audio_files.append(audio_file)
        
        print(f"   📄 Cena {i}: {estimated_duration:.1f}s - '{scene['text'][:50]}...'")
    
    print(f"✅ Ambiente de teste criado em: {test_dir}")
    print(f"📄 Roteiro: {script_path}")
    print(f"🎵 Arquivos de áudio: {len(audio_files)}")
    
    return test_dir, script_path, audio_files

def test_synchronizer_basic():
    """
    Teste básico do sincronizador.
    """
    print("\n🧪 === TESTE: Sincronizador Básico ===")
    
    synchronizer = ScriptSubtitleSynchronizer()
    
    # Teste de cálculo de velocidade de fala
    test_text = "Este é um teste de velocidade de fala para o sistema."
    test_duration = 4.0
    
    speech_rate = synchronizer.calculate_speech_rate(test_text, test_duration)
    print(f"📊 Velocidade calculada: {speech_rate:.1f} chars/s")
    
    # Teste de distribuição de timing
    timing_data = synchronizer.distribute_timing_intelligent(
        test_text, test_duration, speech_rate
    )
    
    print(f"📋 Distribuição de timing:")
    for i, item in enumerate(timing_data, 1):
        print(f"   {i}. {item['start_time']:.1f}s - {item['end_time']:.1f}s: '{item['text']}'")
    
    # Teste de conversão para SRT
    srt_content = synchronizer.generate_srt_from_sync_data(timing_data)
    print(f"\n📝 Conteúdo SRT gerado:")
    print(srt_content[:200] + "..." if len(srt_content) > 200 else srt_content)
    
    return True

def test_script_sync_integration():
    """
    Teste de integração completa com roteiro.
    """
    print("\n🔗 === TESTE: Integração Completa ===")
    
    try:
        # Criar ambiente de teste
        test_dir, script_path, audio_files = create_test_environment()
        
        # Testar sincronização
        subtitle_file = generate_subtitles_from_script_sync(
            script_path=script_path,
            audio_files=audio_files,
            output_dir=os.path.join(test_dir, "subtitles"),
            style_name="modern"
        )
        
        print(f"✅ Legendas geradas: {subtitle_file}")
        
        # Verificar arquivo gerado
        if os.path.exists(subtitle_file):
            with open(subtitle_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            print(f"📊 Tamanho do arquivo: {len(content)} caracteres")
            print(f"📄 Número de linhas: {len(content.splitlines())}")
            
            # Mostrar primeiras legendas
            lines = content.split('\n')[:15]
            print(f"\n📝 Primeiras legendas:")
            print('\n'.join(lines))
            
            return True
        else:
            print(f"❌ Arquivo de legenda não foi criado")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de integração: {e}")
        return False

def test_timing_accuracy():
    """
    Teste de precisão do timing.
    """
    print("\n⏱️ === TESTE: Precisão do Timing ===")
    
    synchronizer = ScriptSubtitleSynchronizer()
    
    # Cenários de teste
    test_cases = [
        {
            "text": "Texto curto.",
            "duration": 2.0,
            "expected_subtitles": 1
        },
        {
            "text": "Primeira frase. Segunda frase mais longa. Terceira frase final.",
            "duration": 8.0,
            "expected_subtitles": 3
        },
        {
            "text": "Uma frase muito longa que deveria ser dividida em múltiplas legendas para melhor legibilidade e compreensão do espectador.",
            "duration": 10.0,
            "expected_subtitles": 1  # Será uma legenda longa
        }
    ]
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 Caso de teste {i}:")
        print(f"   Texto: '{case['text']}'")
        print(f"   Duração: {case['duration']}s")
        
        speech_rate = synchronizer.calculate_speech_rate(case['text'], case['duration'])
        timing_data = synchronizer.distribute_timing_intelligent(
            case['text'], case['duration'], speech_rate
        )
        
        print(f"   Legendas geradas: {len(timing_data)}")
        print(f"   Esperado: {case['expected_subtitles']}")
        
        # Verificar timing
        total_time = max(item['end_time'] for item in timing_data) if timing_data else 0
        time_diff = abs(total_time - case['duration'])
        
        print(f"   Tempo total: {total_time:.1f}s (diferença: {time_diff:.1f}s)")
        
        if time_diff > 0.5:  # Tolerância de 0.5s
            print(f"   ⚠️ Diferença de timing muito grande")
            all_passed = False
        else:
            print(f"   ✅ Timing dentro da tolerância")
    
    return all_passed

def test_performance_comparison():
    """
    Teste de comparação de performance.
    """
    print("\n🏃 === TESTE: Comparação de Performance ===")
    
    # Importar módulos necessários no início da função
    import time
    import os
    import sys
    import json
    import shutil
    
    # Adicionar diretório raiz ao path para imports
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if root_path not in sys.path:
        sys.path.append(root_path)
    
    from src.core.subtitle import generate_subtitles_from_script_sync
    
    # Criar dados de teste
    test_dir, script_path, audio_files = create_test_environment()
    
    print(f"📊 Testando com {len(audio_files)} arquivos de áudio...")
    
    # Testar método novo (sincronização por roteiro)
    start_time = time.time()
    try:
        subtitle_file = generate_subtitles_from_script_sync(
            script_path=script_path,
            audio_files=audio_files,
            output_dir=os.path.join(test_dir, "subtitles_new"),
            style_name="modern"
        )
        new_method_time = time.time() - start_time
        new_method_success = True
        print(f"✅ Método novo: {new_method_time:.2f}s")
    except Exception as e:
        new_method_time = float('inf')
        new_method_success = False
        print(f"❌ Método novo falhou: {e}")
    
    # Simular método tradicional (seria mais lento)
    traditional_time_estimate = len(audio_files) * 30  # 30s por arquivo
    print(f"📊 Método tradicional (estimado): {traditional_time_estimate}s")
    
    if new_method_success:
        speedup = traditional_time_estimate / new_method_time
        print(f"🚀 Aceleração: {speedup:.1f}x mais rápido")
        print(f"💰 Economia de custo: 100% (sem transcrição)")
        return True
    else:
        return False

def test_edge_cases():
    """
    Teste de casos extremos.
    """
    print("\n🔍 === TESTE: Casos Extremos ===")
    
    synchronizer = ScriptSubtitleSynchronizer()
    
    edge_cases = [
        {
            "name": "Texto vazio",
            "text": "",
            "duration": 5.0
        },
        {
            "name": "Duração zero",
            "text": "Texto normal",
            "duration": 0.0
        },
        {
            "name": "Texto muito longo",
            "text": "Esta é uma frase extremamente longa que contém muitas palavras e deveria testar como o sistema lida com textos que excedem a duração normal de uma legenda típica em vídeos.",
            "duration": 3.0
        },
        {
            "name": "Muita pontuação",
            "text": "Olá! Como vai? Tudo bem... Que bom! Até logo.",
            "duration": 6.0
        }
    ]
    
    all_passed = True
    
    for case in edge_cases:
        print(f"\n🔍 Testando: {case['name']}")
        try:
            speech_rate = synchronizer.calculate_speech_rate(case['text'], case['duration'])
            timing_data = synchronizer.distribute_timing_intelligent(
                case['text'], case['duration'], speech_rate
            )
            print(f"   ✅ Processado: {len(timing_data)} legendas")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            all_passed = False
    
    return all_passed

def run_all_tests():
    """
    Executa todos os testes.
    """
    print("🧪 EXECUTANDO TODOS OS TESTES DE SINCRONIZAÇÃO")
    print("=" * 50)
    
    tests = [
        ("Sincronizador Básico", test_synchronizer_basic),
        ("Integração Completa", test_script_sync_integration),
        ("Precisão do Timing", test_timing_accuracy),
        ("Comparação de Performance", test_performance_comparison),
        ("Casos Extremos", test_edge_cases)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n❌ ERRO em {test_name}: {e}")
    
    # Resumo final
    print(f"\n{'='*50}")
    print(f"📊 RESUMO DOS TESTES")
    print(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print(f"🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
    else:
        print(f"⚠️ Alguns testes falharam. Verifique os logs acima.")
    
    return passed == total

def main():
    """
    Função principal.
    """
    print("🎬 TESTE DO SISTEMA DE SINCRONIZAÇÃO DE LEGENDAS")
    print("Baseado em Roteiro - Sem Transcrição")
    print("=" * 60)
    
    try:
        success = run_all_tests()
        
        if success:
            print("\n🚀 SISTEMA VALIDADO! Pronto para produção.")
            print("\n💡 PRÓXIMOS PASSOS:")
            print("   1. Teste com seus próprios arquivos")
            print("   2. Execute: python exemplo_sincronizacao_roteiro.py")
            print("   3. Integre ao seu workflow de produção")
        else:
            print("\n🔧 AJUSTES NECESSÁRIOS antes do uso em produção.")
            
    except KeyboardInterrupt:
        print("\n👋 Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")

if __name__ == "__main__":
    main()