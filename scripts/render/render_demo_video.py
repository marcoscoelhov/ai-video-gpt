#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para renderizar vídeo de demonstração com legendas sincronizadas
"""

import os
import json
from core.imagegen import generate_images_from_prompts
from core.assemble import assemble_video

def main():
    print("🎬 Renderizando vídeo de demonstração...")
    
    # Carregar roteiro
    script_path = 'demo_output/roteiro_ia.json'
    with open(script_path, 'r', encoding='utf-8') as f:
        script = json.load(f)
    
    # Criar diretório de imagens
    images_dir = 'demo_output/images'
    os.makedirs(images_dir, exist_ok=True)
    
    # Gerar imagens
    print("🖼️ Gerando imagens...")
    try:
        # Extrair prompts das descrições visuais
        prompts = [scene['visual_description'] for scene in script['scenes']]
        generated_paths = generate_images_from_prompts(prompts, images_dir)
        
        if generated_paths:
            print("✅ Imagens geradas com sucesso!")
        else:
            raise Exception("Falha na geração de imagens")
    except Exception as e:
        print(f"❌ Erro ao gerar imagens: {e}")
        print("🔄 Criando imagens placeholder...")
        
        # Criar imagens placeholder
        from PIL import Image, ImageDraw, ImageFont
        
        for i, scene in enumerate(script['scenes'], 1):
            img = Image.new('RGB', (720, 1280), color=(50, 50, 50))
            draw = ImageDraw.Draw(img)
            
            # Texto da cena
            text = f"Cena {i}\n\n{scene['visual_description'][:100]}..."
            
            try:
                # Tentar usar fonte padrão
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Desenhar texto centralizado
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (720 - text_width) // 2
            y = (1280 - text_height) // 2
            
            draw.multiline_text((x, y), text, fill=(255, 255, 255), font=font, align='center')
            
            # Salvar imagem
            img_path = os.path.join(images_dir, f'scene_{i}.png')
            img.save(img_path)
            print(f"   - Criada: scene_{i}.png")
    
    # Preparar caminhos
    image_paths = [os.path.join(images_dir, f'scene_{i}.png') for i in range(1, 6)]
    audio_paths = [f'demo_output/audio/scene_0{i}.mp3' for i in range(1, 6)]
    subtitle_path = 'demo_output/subtitles/subtitles.srt'
    output_path = 'demo_video_teste.mp4'
    
    # Verificar arquivos
    print("\n📁 Verificando arquivos:")
    for i, (img, audio) in enumerate(zip(image_paths, audio_paths), 1):
        img_exists = "✅" if os.path.exists(img) else "❌"
        audio_exists = "✅" if os.path.exists(audio) else "❌"
        print(f"   Cena {i}: Imagem {img_exists} | Áudio {audio_exists}")
    
    # Renderizar vídeo
    print("\n🎥 Montando vídeo final...")
    result = assemble_video(
        image_paths=image_paths,
        audio_paths=audio_paths,
        subtitle_path=subtitle_path,
        final_video_path=output_path,
        subtitle_style="modern",
        script_path=script_path,
        use_script_sync=True
    )
    
    if result:
        print(f"\n🎉 Vídeo renderizado com sucesso: {result}")
        print(f"📁 Localização: {os.path.abspath(result)}")
        
        # Verificar tamanho do arquivo
        if os.path.exists(result):
            size_mb = os.path.getsize(result) / (1024 * 1024)
            print(f"📊 Tamanho: {size_mb:.1f} MB")
    else:
        print("❌ Falha na renderização do vídeo")

if __name__ == "__main__":
    main()