import os
import json
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy import concatenate_audioclips, concatenate_videoclips
from moviepy.video.tools.subtitles import TextClip
from .subtitle_styles import SubtitleStyleManager, SubtitleStyle
from .subtitle_moviepy import integrate_moviepy_subtitles
from .video_effects import apply_video_effects, get_available_presets

def get_audio_duration(audio_path):
    """Gets the duration of an audio file using MoviePy."""
    try:
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        audio_clip.close()
        return duration
    except Exception as e:
        print(f"Error getting audio duration with MoviePy: {e}")
        return 0.0

def concatenate_audios(audio_paths, output_path):
    """
    Concatenates multiple audio files into a single one using MoviePy.
    """
    if not audio_paths:
        return None

    try:
        print(f"  -> Concatenating audio files to {output_path}...")
        
        # Load all audio clips
        audio_clips = []
        for audio_path in audio_paths:
            if os.path.exists(audio_path):
                clip = AudioFileClip(audio_path)
                audio_clips.append(clip)
            else:
                print(f"Warning: Audio file not found: {audio_path}")
        
        if not audio_clips:
            print("Error: No valid audio files found.")
            return None
        
        # Concatenate all audio clips
        final_audio = concatenate_audioclips(audio_clips)
        
        # Write the concatenated audio
        final_audio.write_audiofile(output_path, logger=None)
        
        # Clean up clips
        for clip in audio_clips:
            clip.close()
        final_audio.close()
        
        print(f"     - Audio concatenation successful.")
        return output_path
        
    except Exception as e:
        print(f"     - Error during audio concatenation: {e}")
        return None

def assemble_video(image_paths, audio_paths, subtitle_path, final_video_path, 
                  subtitle_style="modern", script_path=None, use_script_sync=True,
                  effects_preset="professional", enable_effects=True, custom_effects_config=None):
    """
    Assembles a video from a list of images, a list of audio files (one per image/scene),
    and a subtitle file with professional styling using MoviePy.
    
    Args:
        image_paths: List of image file paths
        audio_paths: List of audio file paths
        subtitle_path: Path to subtitle file (pode ser None se usar script_sync)
        final_video_path: Output video path
        subtitle_style: Style name or SubtitleStyle object ('netflix', 'youtube', 'cinema', 'modern', 'accessibility')
        script_path: Path to script.json file (para sincronização baseada em roteiro)
        use_script_sync: Se True, usa sincronização baseada no roteiro (recomendado)
        effects_preset: Preset de efeitos visuais ('professional', 'dynamic', 'cinematic', 'energetic')
        enable_effects: Se True, aplica efeitos visuais e transições
        custom_effects_config: Configuração customizada de efeitos (sobrescreve preset)
    """
    # Debug: mostrar quantos arquivos temos
    print(f"     - Imagens encontradas: {len(image_paths) if image_paths else 0}")
    print(f"     - Áudios encontrados: {len(audio_paths) if audio_paths else 0}")
    
    if not image_paths or not audio_paths:
        print("Error: No image or audio files provided.")
        return None
    
    # Ajustar listas para ter o mesmo tamanho (usar o menor número)
    min_count = min(len(image_paths), len(audio_paths))
    if len(image_paths) != len(audio_paths):
        print(f"Warning: Mismatch in number of images ({len(image_paths)}) and audio files ({len(audio_paths)}).")
        print(f"Using first {min_count} files from each list.")
        image_paths = image_paths[:min_count]
        audio_paths = audio_paths[:min_count]

    try:
        print(f"  -> Assembling video to {final_video_path}...")
        
        # Create video clips with effects if enabled
        if enable_effects:
            print(f"     - Aplicando efeitos visuais (preset: {effects_preset})...")
            video_clips = apply_video_effects(
                image_paths=image_paths,
                audio_paths=audio_paths,
                preset=effects_preset,
                custom_config=custom_effects_config
            )
        else:
            print(f"     - Criando clipes sem efeitos...")
            # Create video clips from images with corresponding audio durations (método original)
            video_clips = []
            
            for i, (img_path, audio_path) in enumerate(zip(image_paths, audio_paths)):
                if not os.path.exists(img_path):
                    print(f"Warning: Image file not found: {img_path}")
                    continue
                    
                if not os.path.exists(audio_path):
                    print(f"Warning: Audio file not found: {audio_path}")
                    continue
                
                # Get audio duration
                duration = get_audio_duration(audio_path)
                if duration == 0.0:
                    print(f"Warning: Audio duration for {audio_path} is 0. Using default 5 seconds.")
                    duration = 5.0
                
                # Create image clip with duration matching audio
                img_clip = ImageClip(img_path, duration=duration)
                
                # Resize to target resolution (720x1280 for TikTok format)
                img_clip = img_clip.resized((720, 1280))
                
                # Load and attach audio
                audio_clip = AudioFileClip(audio_path)
                img_clip = img_clip.with_audio(audio_clip)
                
                video_clips.append(img_clip)
        
        if not video_clips:
            print("Error: No valid video clips created.")
            return None
        
        # Concatenate all video clips
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        # Apply subtitles - usar sincronização baseada no roteiro se disponível
        subtitle_file_to_use = subtitle_path
        
        # Se usar sincronização baseada no roteiro e tiver script_path
        if use_script_sync and script_path and os.path.exists(script_path):
            try:
                print(f"     - Gerando legendas com sincronização baseada no roteiro...")
                from .subtitle import generate_subtitles_from_script_sync
                
                # Criar diretório de legendas
                subtitle_dir = os.path.join(os.path.dirname(final_video_path), "subtitles")
                os.makedirs(subtitle_dir, exist_ok=True)
                
                # Gerar legendas sincronizadas
                subtitle_file_to_use = generate_subtitles_from_script_sync(
                    script_path=script_path,
                    audio_files=audio_paths,
                    output_dir=subtitle_dir,
                    style_name=subtitle_style
                )
                print(f"     - Legendas sincronizadas geradas: {os.path.basename(subtitle_file_to_use)}")
                
            except Exception as e:
                print(f"     - Erro na sincronização baseada em roteiro: {e}")
                print(f"     - Usando arquivo de legenda fornecido como fallback")
                # Continua com subtitle_path original
        
        # Aplicar legendas se disponível
        if subtitle_file_to_use and os.path.exists(subtitle_file_to_use):
            try:
                # Detectar formato do vídeo baseado no nome do arquivo ou dimensões
                video_format = "standard"
                if "tiktok" in final_video_path.lower() or "9:16" in final_video_path.lower():
                    video_format = "tiktok"
                elif "youtube" in final_video_path.lower():
                    video_format = "youtube"
                
                # Aplicar legendas usando o sistema MoviePy integrado
                final_video = integrate_moviepy_subtitles(
                    final_video, 
                    subtitle_file_to_use, 
                    subtitle_style, 
                    video_format
                )
                
                sync_method = "roteiro" if (use_script_sync and script_path) else "transcrição"
                print(f"     - Legendas aplicadas com sucesso (método: {sync_method}, estilo: {subtitle_style})")
                
            except Exception as e:
                print(f"     - Warning: Could not add subtitles: {e}")
        elif use_script_sync and script_path:
            print(f"     - Aviso: Sincronização baseada em roteiro solicitada, mas não foi possível gerar legendas")
        else:
            print(f"     - Nenhum arquivo de legenda fornecido ou encontrado")
        
        # Write the final video
        final_video.write_videofile(
            final_video_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            logger=None
        )
        
        # Clean up clips
        for clip in video_clips:
            clip.close()
        final_video.close()
        
        print(f"     - Video assembled successfully.")
        return final_video_path
        
    except Exception as e:
        print(f"     - Error during video assembly: {e}")
        return None

# Função auxiliar para manter compatibilidade com código existente
def create_video_from_resources(images_dir, audios_dir, script_path, output_path, 
                              subtitle_style="modern", effects_preset="professional", 
                              enable_effects=True, custom_effects_config=None):
    """
    Função auxiliar para criar vídeo a partir de diretórios de recursos.
    Mantém compatibilidade com o código existente.
    
    Args:
        images_dir: Diretório com imagens
        audios_dir: Diretório com áudios
        script_path: Caminho para o arquivo script.json
        output_path: Caminho para o vídeo de saída
        subtitle_style: Estilo de legendas
        effects_preset: Preset de efeitos visuais ('professional', 'dynamic', 'cinematic', 'energetic')
        enable_effects: Se True, aplica efeitos visuais e transições
        custom_effects_config: Configuração customizada de efeitos (sobrescreve preset)
    """
    try:
        # Carregar script para obter ordem das cenas
        with open(script_path, 'r', encoding='utf-8') as f:
            script_data = json.load(f)
        
        # Construir listas de imagens e áudios na ordem correta
        image_paths = []
        audio_paths = []
        
        for i, scene in enumerate(script_data.get('scenes', [])):
            img_file = f"scene_{i+1}.png"
            audio_file = f"scene_{i+1}.mp3"
            
            img_path = os.path.join(images_dir, img_file)
            audio_path = os.path.join(audios_dir, audio_file)
            
            if os.path.exists(img_path) and os.path.exists(audio_path):
                image_paths.append(img_path)
                audio_paths.append(audio_path)
        
        # Procurar arquivo de legendas
        subtitle_path = None
        possible_subtitle_files = ['subtitles.srt', 'subtitles.ass']
        for subtitle_file in possible_subtitle_files:
            subtitle_candidate = os.path.join(os.path.dirname(script_path), 'subtitles', subtitle_file)
            if os.path.exists(subtitle_candidate):
                subtitle_path = subtitle_candidate
                break
        
        # Montar vídeo com efeitos
        return assemble_video(
            image_paths=image_paths, 
            audio_paths=audio_paths, 
            subtitle_path=subtitle_path, 
            final_video_path=output_path, 
            subtitle_style=subtitle_style,
            script_path=script_path,
            use_script_sync=True,
            effects_preset=effects_preset,
            enable_effects=enable_effects,
            custom_effects_config=custom_effects_config
        )
        
    except Exception as e:
        print(f"Error creating video from resources: {e}")
        return None