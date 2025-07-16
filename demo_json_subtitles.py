#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo de Legendas JSON - Demonstração da funcionalidade de legendas em formato JSON.

Este script demonstra:
1. Como criar legendas JSON manualmente
2. Conversão entre formatos JSON e SRT
3. Vantagens do formato JSON sobre SRT
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gemini_subtitle_client import GeminiSubtitleClient

def create_sample_json_subtitles():
    """Cria um exemplo de legendas em formato JSON."""
    return {
        "subtitles": [
            {
                "id": 1,
                "start_time": "00:00:00.000",
                "end_time": "00:00:03.500",
                "text": "Bem-vindos ao futuro da criação de vídeos!",
                "speaker": "Narrador",
                "confidence": 0.95
            },
            {
                "id": 2,
                "start_time": "00:00:04.000",
                "end_time": "00:00:07.200",
                "text": "Com inteligência artificial, podemos gerar legendas precisas.",
                "speaker": "Narrador",
                "confidence": 0.92
            },
            {
                "id": 3,
                "start_time": "00:00:07.500",
                "end_time": "00:00:10.800",
                "text": "O formato JSON oferece muito mais flexibilidade.",
                "speaker": "Narrador",
                "confidence": 0.98
            },
            {
                "id": 4,
                "start_time": "00:00:11.000",
                "end_time": "00:00:14.500",
                "text": "Podemos incluir metadados como confiança e identificação do falante.",
                "speaker": "Narrador",
                "confidence": 0.89
            }
        ],
        "metadata": {
            "language": "pt-BR",
            "total_duration": "00:00:14.500",
            "created_at": datetime.now().isoformat(),
            "model": "gemini-1.5-flash",
            "audio_quality": "high",
            "speaker_count": 1,
            "average_confidence": 0.935
        }
    }

def demo_json_advantages():
    """Demonstra as vantagens do formato JSON sobre SRT."""
    
    print("🎬 Demo: Vantagens das Legendas JSON")
    print("=" * 50)
    
    # Criar cliente
    client = GeminiSubtitleClient()
    
    # 1. Criar legendas JSON de exemplo
    print("\n📝 1. Criando legendas JSON com metadados ricos...")
    json_subtitles = create_sample_json_subtitles()
    
    print("✅ Legendas JSON criadas!")
    print(f"   - Total de legendas: {len(json_subtitles['subtitles'])}")
    print(f"   - Idioma: {json_subtitles['metadata']['language']}")
    print(f"   - Confiança média: {json_subtitles['metadata']['average_confidence']:.1%}")
    print(f"   - Número de falantes: {json_subtitles['metadata']['speaker_count']}")
    
    # Mostrar estrutura JSON
    print("\n📋 Estrutura JSON (primeiras 2 legendas):")
    for subtitle in json_subtitles["subtitles"][:2]:
        print(f"   ID {subtitle['id']}: {subtitle['start_time']} → {subtitle['end_time']}")
        print(f"      Texto: {subtitle['text']}")
        print(f"      Falante: {subtitle['speaker']}")
        print(f"      Confiança: {subtitle['confidence']:.1%}")
        print()
    
    # 2. Salvar JSON
    print("💾 2. Salvando legendas JSON...")
    json_file = Path("demo_subtitles.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_subtitles, f, indent=2, ensure_ascii=False)
    print(f"✅ Salvo em: {json_file}")
    
    # 3. Converter para SRT
    print("\n🔄 3. Convertendo JSON para SRT...")
    srt_content = client.json_to_srt(json_subtitles)
    
    srt_file = Path("demo_subtitles.srt")
    with open(srt_file, 'w', encoding='utf-8') as f:
        f.write(srt_content)
    print(f"✅ SRT gerado: {srt_file}")
    
    # Mostrar SRT gerado
    print("\n📋 SRT gerado (primeiras linhas):")
    lines = srt_content.split('\n')[:12]
    for line in lines:
        print(f"   {line}")
    
    # 4. Converter SRT de volta para JSON
    print("\n🔄 4. Convertendo SRT de volta para JSON...")
    json_from_srt = client.srt_to_json(srt_content)
    
    json_from_srt_file = Path("demo_subtitles_from_srt.json")
    with open(json_from_srt_file, 'w', encoding='utf-8') as f:
        json.dump(json_from_srt, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON reconstruído: {json_from_srt_file}")
    
    # 5. Comparar formatos
    print("\n📊 5. Comparação de formatos:")
    print("\n🔹 Vantagens do JSON:")
    print("   ✅ Metadados ricos (confiança, falante, modelo usado)")
    print("   ✅ Estrutura hierárquica clara")
    print("   ✅ Fácil de processar programaticamente")
    print("   ✅ Extensível (pode adicionar novos campos)")
    print("   ✅ Suporte nativo a Unicode")
    print("   ✅ Validação de esquema possível")
    
    print("\n🔹 Limitações do SRT:")
    print("   ❌ Apenas texto, timestamps e numeração")
    print("   ❌ Sem metadados")
    print("   ❌ Formato rígido")
    print("   ❌ Problemas com caracteres especiais")
    print("   ❌ Difícil de estender")
    
    # 6. Análise de dados
    print("\n📈 6. Análise de dados (possível apenas com JSON):")
    
    # Estatísticas que só são possíveis com JSON
    confidences = [sub['confidence'] for sub in json_subtitles['subtitles']]
    durations = []
    
    for sub in json_subtitles['subtitles']:
        start = sub['start_time']
        end = sub['end_time']
        # Calcular duração (simplificado)
        start_sec = float(start.split(':')[-1])
        end_sec = float(end.split(':')[-1])
        durations.append(end_sec - start_sec)
    
    print(f"   📊 Confiança mínima: {min(confidences):.1%}")
    print(f"   📊 Confiança máxima: {max(confidences):.1%}")
    print(f"   📊 Duração média por legenda: {sum(durations)/len(durations):.1f}s")
    print(f"   📊 Legenda mais longa: {max(durations):.1f}s")
    print(f"   📊 Legenda mais curta: {min(durations):.1f}s")
    
    # 7. Tamanhos de arquivo
    print("\n💾 7. Comparação de tamanhos:")
    json_size = json_file.stat().st_size
    srt_size = srt_file.stat().st_size
    
    print(f"   📄 JSON: {json_size} bytes")
    print(f"   📄 SRT: {srt_size} bytes")
    print(f"   📊 Diferença: {json_size - srt_size:+d} bytes ({((json_size/srt_size-1)*100):+.1f}%)")
    
    print("\n🎯 Conclusão:")
    print("   O formato JSON oferece muito mais valor para aplicações modernas,")
    print("   permitindo análises avançadas e metadados ricos, com um pequeno")
    print("   overhead de tamanho que é compensado pela funcionalidade adicional.")
    
    print("\n🏁 Demo concluída!")
    print("=" * 50)

def demo_real_audio():
    """Demonstra geração de legendas JSON a partir de áudio real."""
    
    print("\n🎵 Demo: Geração de Legendas JSON a partir de Áudio")
    print("=" * 50)
    
    # Procurar por arquivos de áudio existentes
    audio_files = []
    
    # Procurar em output/*/audio/
    output_dir = Path("output")
    if output_dir.exists():
        for project_dir in output_dir.iterdir():
            if project_dir.is_dir():
                audio_dir = project_dir / "audio"
                if audio_dir.exists():
                    audio_files.extend(list(audio_dir.glob("*.mp3")))
    
    if not audio_files:
        print("❌ Nenhum arquivo de áudio encontrado")
        print("💡 Execute o main.py primeiro para gerar alguns projetos.")
        return
    
    # Usar o primeiro arquivo encontrado
    audio_file = audio_files[0]
    print(f"🎵 Usando arquivo: {audio_file}")
    
    # Gerar legendas JSON
    client = GeminiSubtitleClient()
    
    print("\n📝 Gerando legendas JSON...")
    try:
        json_subtitles = client.generate_subtitles_json(str(audio_file))
        
        if json_subtitles and json_subtitles.get('subtitles'):
            print(f"✅ Legendas geradas com sucesso!")
            print(f"   - Total: {len(json_subtitles['subtitles'])} legendas")
            
            # Salvar resultado
            output_file = Path("real_audio_subtitles.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_subtitles, f, indent=2, ensure_ascii=False)
            
            print(f"   - Salvo em: {output_file}")
            
            # Mostrar algumas legendas
            print("\n📋 Primeiras legendas geradas:")
            for i, sub in enumerate(json_subtitles['subtitles'][:3]):
                print(f"   {sub.get('id', i+1)}: {sub.get('start_time')} → {sub.get('end_time')}")
                print(f"      {sub.get('text', '')[:60]}...")
        else:
            print("❌ Falha na geração de legendas")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    # Executar demos
    demo_json_advantages()
    demo_real_audio()