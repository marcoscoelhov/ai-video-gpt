#!/usr/bin/env python3
"""
Modo de Teste - Reutiliza arquivos existentes para economizar créditos

Este script permite testar a funcionalidade de montagem de vídeo
sem gastar créditos de API, reutilizando arquivos já gerados.
"""

import os
import sys
import argparse
from datetime import datetime
from src.assemble import assemble_video

def list_available_projects():
    """Lista todos os projetos disponíveis para reutilização."""
    output_dir = "output"
    projects = []
    
    if not os.path.exists(output_dir):
        print("❌ Diretório 'output' não encontrado.")
        return projects
    
    for item in os.listdir(output_dir):
        item_path = os.path.join(output_dir, item)
        if os.path.isdir(item_path) and item.startswith("video_"):
            # Verificar se tem todos os arquivos necessários
            images_dir = os.path.join(item_path, "images")
            audio_dir = os.path.join(item_path, "audio")
            subtitles_dir = os.path.join(item_path, "subtitles")
            
            if all(os.path.exists(d) for d in [images_dir, audio_dir, subtitles_dir]):
                # Contar arquivos
                images = [f for f in os.listdir(images_dir) if f.endswith('.png')]
                audios = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
                subtitles = [f for f in os.listdir(subtitles_dir) if f.endswith('.srt')]
                
                if images and audios and subtitles and len(images) == len(audios):
                    projects.append({
                        'name': item,
                        'path': item_path,
                        'scenes': len(images),
                        'images': images,
                        'audios': audios
                    })
    
    return projects

def test_video_assembly(project_path, output_name=None):
    """Testa a montagem de vídeo usando arquivos existentes."""
    print(f"🧪 Iniciando teste de montagem para: {os.path.basename(project_path)}")
    
    # Caminhos dos diretórios
    images_dir = os.path.join(project_path, "images")
    audio_dir = os.path.join(project_path, "audio")
    subtitles_dir = os.path.join(project_path, "subtitles")
    
    # Listar e ordenar arquivos
    image_files = sorted([f for f in os.listdir(images_dir) if f.endswith('.png')])
    audio_files = sorted([f for f in os.listdir(audio_dir) if f.endswith('.mp3')])
    subtitle_file = next((f for f in os.listdir(subtitles_dir) if f.endswith('.srt')), None)
    
    if not subtitle_file:
        print("❌ Arquivo de legendas não encontrado.")
        return False
    
    # Criar caminhos absolutos
    image_paths = [os.path.abspath(os.path.join(images_dir, img)) for img in image_files]
    audio_paths = [os.path.abspath(os.path.join(audio_dir, aud)) for aud in audio_files]
    subtitle_path = os.path.abspath(os.path.join(subtitles_dir, subtitle_file))
    
    # Nome do vídeo de saída
    if not output_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"test_video_{timestamp}.mp4"
    
    final_video_path = os.path.abspath(os.path.join(project_path, output_name))
    
    print(f"📁 Usando {len(image_paths)} imagens e {len(audio_paths)} áudios")
    print(f"📜 Legendas: {subtitle_file}")
    print(f"🎬 Vídeo final: {output_name}")
    
    # Executar montagem
    try:
        result = assemble_video(image_paths, audio_paths, subtitle_path, final_video_path)
        
        if result:
            print(f"✅ Teste concluído com sucesso!")
            print(f"📹 Vídeo salvo em: {result}")
            
            # Verificar se o arquivo foi criado
            if os.path.exists(result):
                file_size = os.path.getsize(result) / (1024 * 1024)  # MB
                print(f"📊 Tamanho do arquivo: {file_size:.2f} MB")
            
            return True
        else:
            print("❌ Falha na montagem do vídeo.")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Modo de teste - reutiliza arquivos existentes")
    parser.add_argument("--project", "-p", help="Nome do projeto para reutilizar")
    parser.add_argument("--list", "-l", action="store_true", help="Listar projetos disponíveis")
    parser.add_argument("--output", "-o", help="Nome do arquivo de vídeo de saída")
    
    args = parser.parse_args()
    
    # Listar projetos disponíveis
    projects = list_available_projects()
    
    if args.list or not args.project:
        print("📋 Projetos disponíveis para reutilização:")
        print()
        
        if not projects:
            print("❌ Nenhum projeto completo encontrado.")
            print("💡 Execute o main.py primeiro para gerar alguns projetos.")
            return
        
        for i, project in enumerate(projects, 1):
            print(f"{i}. {project['name']}")
            print(f"   📁 {project['scenes']} cenas")
            print(f"   🖼️  Imagens: {', '.join(project['images'])}")
            print(f"   🎵 Áudios: {', '.join(project['audios'])}")
            print()
        
        if not args.project:
            print("💡 Use --project <nome> para testar um projeto específico")
            return
    
    # Encontrar projeto especificado
    selected_project = None
    for project in projects:
        if args.project in project['name'] or project['name'].endswith(args.project):
            selected_project = project
            break
    
    if not selected_project:
        print(f"❌ Projeto '{args.project}' não encontrado.")
        print("💡 Use --list para ver projetos disponíveis.")
        return
    
    # Executar teste
    print(f"🚀 Executando teste com projeto: {selected_project['name']}")
    print("💰 Custo: R$ 0,00 (reutilizando arquivos existentes)")
    print()
    
    success = test_video_assembly(selected_project['path'], args.output)
    
    if success:
        print()
        print("🎉 Teste concluído com sucesso!")
        print("💡 Agora você pode fazer ajustes no código sem gastar créditos.")
    else:
        print()
        print("❌ Teste falhou. Verifique os logs acima para detalhes.")

if __name__ == "__main__":
    main()