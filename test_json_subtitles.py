#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para demonstrar o uso de legendas em formato JSON.

Este script testa:
1. Geração de legendas JSON usando o Gemini
2. Conversão entre formatos JSON e SRT
3. Montagem de vídeo com legendas JSON
"""

import os
import sys
import json
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gemini_subtitle_client import GeminiSubtitleClient
from assemble import assemble_video

def test_json_subtitles():
    """Testa a funcionalidade de legendas JSON."""
    
    print("🎬 Teste de Legendas JSON")
    print("=" * 50)
    
    # Configurar cliente Gemini
    client = GeminiSubtitleClient()
    
    # Verificar se há projetos disponíveis no diretório output
    output_dir = Path("output")
    if not output_dir.exists():
        print("❌ Diretório 'output' não encontrado")
        return
    
    # Listar projetos disponíveis (similar ao test_mode.py)
    projects = []
    for item in output_dir.iterdir():
        if item.is_dir() and item.name.startswith("video_"):
            # Verificar se tem todos os arquivos necessários
            images_dir = item / "images"
            audio_dir = item / "audio"
            subtitles_dir = item / "subtitles"
            
            if all(d.exists() for d in [images_dir, audio_dir, subtitles_dir]):
                # Verificar se há arquivos de áudio
                audio_files = list(audio_dir.glob("*.mp3"))
                if audio_files:
                    projects.append({
                        'name': item.name,
                        'path': item,
                        'audio_files': audio_files
                    })
    
    if not projects:
        print("❌ Nenhum projeto completo encontrado")
        print("💡 Execute o main.py primeiro para gerar alguns projetos.")
        return
    
    print("📁 Projetos disponíveis:")
    for i, project in enumerate(projects, 1):
        print(f"  {i}. {project['name']} ({len(project['audio_files'])} áudios)")
    
    # Usar o primeiro projeto para teste
    selected_project = projects[0]
    project_name = selected_project['name']
    project_path = selected_project['path']
    
    print(f"\n🎯 Usando projeto: {project_name}")
    
    # Usar o primeiro arquivo de áudio encontrado
    audio_file = selected_project['audio_files'][0]
    print(f"🎵 Arquivo de áudio encontrado: {audio_file}")
    
    # Teste 1: Gerar legendas JSON
    print("\n📝 Teste 1: Gerando legendas JSON...")
    try:
        subtitle_json = client.generate_subtitles_json(str(audio_file))
        
        if subtitle_json and "subtitles" in subtitle_json:
            print(f"✅ Legendas JSON geradas com sucesso!")
            print(f"   - Total de legendas: {len(subtitle_json['subtitles'])}")
            
            # Salvar JSON
            json_file = project_path / "subtitles.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(subtitle_json, f, indent=2, ensure_ascii=False)
            print(f"   - Salvo em: {json_file}")
            
            # Mostrar exemplo das primeiras legendas
            if subtitle_json["subtitles"]:
                print("\n📋 Exemplo das primeiras legendas:")
                for i, sub in enumerate(subtitle_json["subtitles"][:3]):
                    print(f"   {sub.get('id', i+1)}: {sub.get('start_time')} --> {sub.get('end_time')}")
                    print(f"      {sub.get('text', '')[:50]}...")
        else:
            print("❌ Falha ao gerar legendas JSON")
            return
            
    except Exception as e:
        print(f"❌ Erro ao gerar legendas JSON: {e}")
        return
    
    # Teste 2: Converter JSON para SRT
    print("\n🔄 Teste 2: Convertendo JSON para SRT...")
    try:
        srt_content = client.json_to_srt(subtitle_json)
        
        if srt_content:
            print("✅ Conversão JSON → SRT bem-sucedida!")
            
            # Salvar SRT
            srt_file = project_path / "subtitles_from_json.srt"
            with open(srt_file, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            print(f"   - Salvo em: {srt_file}")
            
            # Mostrar exemplo do SRT
            print("\n📋 Exemplo do SRT gerado:")
            lines = srt_content.split('\n')[:10]
            for line in lines:
                print(f"   {line}")
        else:
            print("❌ Falha na conversão JSON → SRT")
            
    except Exception as e:
        print(f"❌ Erro na conversão JSON → SRT: {e}")
    
    # Teste 3: Converter SRT de volta para JSON
    print("\n🔄 Teste 3: Convertendo SRT de volta para JSON...")
    try:
        json_from_srt = client.srt_to_json(srt_content)
        
        if json_from_srt and "subtitles" in json_from_srt:
            print("✅ Conversão SRT → JSON bem-sucedida!")
            print(f"   - Total de legendas: {len(json_from_srt['subtitles'])}")
            
            # Comparar com o JSON original
            original_count = len(subtitle_json["subtitles"])
            converted_count = len(json_from_srt["subtitles"])
            
            if original_count == converted_count:
                print("✅ Número de legendas mantido na conversão")
            else:
                print(f"⚠️ Diferença no número de legendas: {original_count} → {converted_count}")
        else:
            print("❌ Falha na conversão SRT → JSON")
            
    except Exception as e:
        print(f"❌ Erro na conversão SRT → JSON: {e}")
    
    # Teste 4: Montar vídeo com legendas
    print("\n🎬 Teste 4: Montando vídeo com legendas...")
    try:
        output_name = "video_json_test.mp4"
        
        print(f"   - Projeto: {project_name}")
        print(f"   - Saída: {output_name}")
        
        # Preparar caminhos para assemble_video
        images_dir = project_path / "images"
        audio_dir = project_path / "audio"
        subtitles_dir = project_path / "subtitles"
        
        # Listar e ordenar arquivos
        image_files = sorted(list(images_dir.glob("*.png")))
        audio_files = sorted(list(audio_dir.glob("*.mp3")))
        
        # Usar o arquivo SRT convertido do JSON
        subtitle_file = project_path / "subtitles_from_json.srt"
        if not subtitle_file.exists():
            # Fallback para arquivo SRT original
            subtitle_files = list(subtitles_dir.glob("*.srt"))
            subtitle_file = subtitle_files[0] if subtitle_files else None
        
        if not subtitle_file:
            print("❌ Arquivo de legendas não encontrado")
            return
        
        # Caminho do vídeo final
        final_video_path = project_path / output_name
        
        print(f"   - Imagens: {len(image_files)}")
        print(f"   - Áudios: {len(audio_files)}")
        print(f"   - Legendas: {subtitle_file.name}")
        
        # Converter paths para strings
        image_paths = [str(img) for img in image_files]
        audio_paths = [str(aud) for aud in audio_files]
        
        success = assemble_video(image_paths, audio_paths, str(subtitle_file), str(final_video_path))
        
        if success:
            print("✅ Vídeo montado com sucesso!")
            if final_video_path.exists():
                size_mb = final_video_path.stat().st_size / (1024 * 1024)
                print(f"   - Arquivo: {final_video_path}")
                print(f"   - Tamanho: {size_mb:.1f} MB")
        else:
            print("❌ Falha na montagem do vídeo")
            
    except Exception as e:
        print(f"❌ Erro na montagem do vídeo: {e}")
    
    print("\n🏁 Teste concluído!")
    print("=" * 50)

if __name__ == "__main__":
    test_json_subtitles()