#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script final para renderizar vídeo de demonstração usando o sistema existente
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont
from core.assemble import assemble_video

def create_demo_images(script, images_dir):
    """Cria imagens de demonstração para o vídeo."""
    os.makedirs(images_dir, exist_ok=True)
    image_paths = []
    
    print("🖼️ Criando imagens de demonstração...")
    
    for i, scene in enumerate(script['scenes'], 1):
        # Criar imagem com gradiente
        img = Image.new('RGB', (720, 1280), color=(20, 30, 60))
        draw = ImageDraw.Draw(img)
        
        # Gradiente simples
        for y in range(1280):
            color_intensity = int(20 + (y / 1280) * 40)
            for x in range(720):
                img.putpixel((x, y), (color_intensity, color_intensity + 10, color_intensity + 30))
        
        draw = ImageDraw.Draw(img)
        
        # Título da cena
        title = f"CENA {i}"
        description = scene['visual_description'][:120] + "..." if len(scene['visual_description']) > 120 else scene['visual_description']
        narration = scene['narration'][:100] + "..." if len(scene['narration']) > 100 else scene['narration']
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            desc_font = ImageFont.truetype("arial.ttf", 24)
            narr_font = ImageFont.truetype("arial.ttf", 20)
        except:
            title_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
            narr_font = ImageFont.load_default()
        
        # Desenhar título
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (720 - title_width) // 2
        draw.text((title_x, 150), title, fill=(255, 255, 255), font=title_font)
        
        # Desenhar linha decorativa
        draw.rectangle([title_x, 220, title_x + title_width, 225], fill=(100, 150, 255))
        
        # Função para quebrar texto em linhas
        def wrap_text(text, font, max_width):
            lines = []
            words = text.split()
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] < max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            return lines
        
        # Desenhar descrição visual
        desc_lines = wrap_text(description, desc_font, 650)
        y_offset = 300
        draw.text((35, y_offset - 30), "DESCRIÇÃO VISUAL:", fill=(150, 200, 255), font=desc_font)
        
        for line in desc_lines[:6]:  # Máximo 6 linhas
            draw.text((35, y_offset), line, fill=(220, 220, 220), font=desc_font)
            y_offset += 35
        
        # Desenhar narração
        y_offset += 50
        draw.text((35, y_offset), "NARRAÇÃO:", fill=(255, 200, 150), font=narr_font)
        y_offset += 40
        
        narr_lines = wrap_text(narration, narr_font, 650)
        for line in narr_lines[:8]:  # Máximo 8 linhas
            draw.text((35, y_offset), line, fill=(200, 200, 200), font=narr_font)
            y_offset += 30
        
        # Adicionar número da cena no canto
        draw.ellipse([620, 50, 670, 100], fill=(100, 150, 255))
        num_bbox = draw.textbbox((0, 0), str(i), font=title_font)
        num_width = num_bbox[2] - num_bbox[0]
        draw.text((645 - num_width//2, 65), str(i), fill=(255, 255, 255), font=title_font)
        
        # Salvar imagem
        img_path = os.path.join(images_dir, f'scene_{i:02d}.png')
        img.save(img_path)
        image_paths.append(img_path)
        print(f"   ✅ Criada: scene_{i:02d}.png")
    
    return image_paths

def create_demo_audio_files(script, audio_dir):
    """Cria arquivos de áudio de demonstração (silêncio)."""
    os.makedirs(audio_dir, exist_ok=True)
    audio_paths = []
    
    print("🔊 Criando arquivos de áudio de demonstração...")
    
    # Usar ffmpeg para criar arquivos de áudio silenciosos
    for i, scene in enumerate(script['scenes'], 1):
        audio_path = os.path.join(audio_dir, f'scene_{i:02d}.mp3')
        
        # Criar 5 segundos de silêncio
        cmd = f'ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -t 5 -y "{audio_path}"'
        
        try:
            os.system(cmd + ' > nul 2>&1')  # Silenciar output
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                audio_paths.append(audio_path)
                print(f"   ✅ Criado: scene_{i:02d}.mp3")
            else:
                print(f"   ❌ Falha ao criar: scene_{i:02d}.mp3")
        except Exception as e:
            print(f"   ❌ Erro ao criar áudio {i}: {e}")
    
    return audio_paths

def main():
    print("🎬 Renderizando vídeo de demonstração final...")
    
    # Carregar roteiro
    script_path = 'demo_output/roteiro_ia.json'
    if not os.path.exists(script_path):
        print(f"❌ Arquivo de roteiro não encontrado: {script_path}")
        return
    
    with open(script_path, 'r', encoding='utf-8') as f:
        script = json.load(f)
    
    print(f"📋 Roteiro carregado: {script['title']}")
    print(f"🎯 Tema: {script['theme']}")
    print(f"🎬 Cenas: {len(script['scenes'])}")
    
    # Criar diretórios
    images_dir = 'demo_output/images'
    audio_dir = 'demo_output/audio'
    
    # Criar imagens
    image_paths = create_demo_images(script, images_dir)
    
    # Criar áudios
    audio_paths = create_demo_audio_files(script, audio_dir)
    
    # Verificar se temos arquivos suficientes
    if len(image_paths) != len(script['scenes']):
        print(f"❌ Erro: Esperado {len(script['scenes'])} imagens, criado {len(image_paths)}")
        return
    
    # Caminhos finais
    subtitle_path = 'demo_output/subtitles/subtitles.srt'
    output_path = 'demo_video_final.mp4'
    
    print("\n📁 Verificando arquivos:")
    for i, (img, audio) in enumerate(zip(image_paths, audio_paths), 1):
        img_exists = "✅" if os.path.exists(img) else "❌"
        audio_exists = "✅" if os.path.exists(audio) else "❌"
        print(f"   Cena {i}: Imagem {img_exists} | Áudio {audio_exists}")
    
    subtitle_exists = "✅" if os.path.exists(subtitle_path) else "❌"
    print(f"   Legendas: {subtitle_exists}")
    
    # Renderizar vídeo
    print("\n🎥 Montando vídeo final...")
    try:
        result = assemble_video(
            image_paths=image_paths,
            audio_paths=audio_paths if audio_paths else None,
            subtitle_path=subtitle_path if os.path.exists(subtitle_path) else None,
            final_video_path=output_path,
            subtitle_style="modern",
            script_path=script_path,
            use_script_sync=True
        )
        
        if result and os.path.exists(result):
            size_mb = os.path.getsize(result) / (1024 * 1024)
            print(f"\n🎉 Vídeo renderizado com sucesso!")
            print(f"📁 Localização: {os.path.abspath(result)}")
            print(f"📊 Tamanho: {size_mb:.1f} MB")
            print(f"⏱️ Duração estimada: {len(image_paths) * 5} segundos")
            print(f"🎬 Cenas: {len(image_paths)}")
            print(f"\n🎯 Funcionalidades demonstradas:")
            print(f"   ✅ Geração de roteiro estruturado")
            print(f"   ✅ Criação de imagens temáticas")
            print(f"   ✅ Sistema de legendas sincronizadas")
            print(f"   ✅ Montagem automática de vídeo")
            print(f"   ✅ Timing preciso baseado no roteiro")
        else:
            print("❌ Falha na renderização do vídeo")
            
    except Exception as e:
        print(f"❌ Erro durante a renderização: {e}")

if __name__ == "__main__":
    main()