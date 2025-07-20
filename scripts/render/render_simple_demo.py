#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificado para renderizar vídeo de demonstração apenas com imagens e legendas
"""

import os
import json
from moviepy.editor import ImageClip, concatenate_videoclips, TextClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_images(script, images_dir):
    """Cria imagens placeholder para o vídeo."""
    os.makedirs(images_dir, exist_ok=True)
    
    for i, scene in enumerate(script['scenes'], 1):
        # Criar imagem placeholder
        img = Image.new('RGB', (720, 1280), color=(30, 30, 50))
        draw = ImageDraw.Draw(img)
        
        # Texto da cena
        title = f"Cena {i}"
        description = scene['visual_description'][:150] + "..." if len(scene['visual_description']) > 150 else scene['visual_description']
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 36)
            desc_font = ImageFont.truetype("arial.ttf", 20)
        except:
            title_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
        
        # Desenhar título
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (720 - title_width) // 2
        draw.text((title_x, 200), title, fill=(255, 255, 255), font=title_font)
        
        # Desenhar descrição
        lines = []
        words = description.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=desc_font)
            if bbox[2] - bbox[0] < 650:  # Largura máxima
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        y_offset = 300
        for line in lines[:8]:  # Máximo 8 linhas
            line_bbox = draw.textbbox((0, 0), line, font=desc_font)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (720 - line_width) // 2
            draw.text((line_x, y_offset), line, fill=(200, 200, 200), font=desc_font)
            y_offset += 35
        
        # Salvar imagem
        img_path = os.path.join(images_dir, f'scene_{i}.png')
        img.save(img_path)
        print(f"   - Criada: scene_{i}.png")
    
    return [os.path.join(images_dir, f'scene_{i}.png') for i in range(1, len(script['scenes']) + 1)]

def create_video_with_subtitles(image_paths, subtitle_path, output_path, duration_per_scene=5):
    """Cria vídeo com imagens e legendas."""
    print("🎬 Criando vídeo com legendas...")
    
    # Criar clips de imagem
    clips = []
    for i, img_path in enumerate(image_paths):
        clip = ImageClip(img_path, duration=duration_per_scene)
        clips.append(clip)
    
    # Concatenar clips
    video = concatenate_videoclips(clips, method="compose")
    
    # Adicionar legendas se existirem
    if os.path.exists(subtitle_path):
        print("📝 Adicionando legendas...")
        try:
            # Ler arquivo SRT
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()
            
            # Parse simples do SRT
            subtitle_clips = []
            blocks = srt_content.strip().split('\n\n')
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    try:
                        # Parse do timing
                        timing = lines[1]
                        start_time, end_time = timing.split(' --> ')
                        
                        # Converter para segundos
                        def time_to_seconds(time_str):
                            h, m, s = time_str.replace(',', '.').split(':')
                            return float(h) * 3600 + float(m) * 60 + float(s)
                        
                        start = time_to_seconds(start_time)
                        end = time_to_seconds(end_time)
                        
                        # Texto da legenda
                        text = ' '.join(lines[2:])
                        
                        # Criar clip de texto
                        txt_clip = TextClip(
                            text,
                            fontsize=24,
                            color='white',
                            stroke_color='black',
                            stroke_width=2,
                            font='Arial-Bold'
                        ).set_position(('center', 'bottom')).set_start(start).set_end(end)
                        
                        subtitle_clips.append(txt_clip)
                        
                    except Exception as e:
                        print(f"   - Erro ao processar legenda: {e}")
                        continue
            
            if subtitle_clips:
                video = CompositeVideoClip([video] + subtitle_clips)
                print(f"   - {len(subtitle_clips)} legendas adicionadas")
            
        except Exception as e:
            print(f"   - Erro ao adicionar legendas: {e}")
    
    # Salvar vídeo
    print("💾 Salvando vídeo...")
    video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac' if video.audio else None,
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        verbose=False,
        logger=None
    )
    
    return output_path

def main():
    print("🎬 Renderizando vídeo de demonstração simplificado...")
    
    # Carregar roteiro
    script_path = 'demo_output/roteiro_ia.json'
    with open(script_path, 'r', encoding='utf-8') as f:
        script = json.load(f)
    
    # Criar imagens
    images_dir = 'demo_output/images'
    print("🖼️ Criando imagens placeholder...")
    image_paths = create_placeholder_images(script, images_dir)
    
    # Caminhos
    subtitle_path = 'demo_output/subtitles/subtitles.srt'
    output_path = 'demo_video_simples.mp4'
    
    # Criar vídeo
    result = create_video_with_subtitles(image_paths, subtitle_path, output_path)
    
    if result and os.path.exists(result):
        size_mb = os.path.getsize(result) / (1024 * 1024)
        print(f"\n🎉 Vídeo criado com sucesso!")
        print(f"📁 Localização: {os.path.abspath(result)}")
        print(f"📊 Tamanho: {size_mb:.1f} MB")
        print(f"⏱️ Duração: {len(image_paths) * 5} segundos")
        print(f"🎬 Cenas: {len(image_paths)}")
    else:
        print("❌ Falha na criação do vídeo")

if __name__ == "__main__":
    main()