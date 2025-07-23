import argparse
import os
import sys
import json
import datetime
from dotenv import load_dotenv

# Import logging system
from src.utils.logger import setup_logging, get_logger, log_video_generation_step, log_performance

# Load environment variables from .env file
load_dotenv()

# Import modules from new organized structure
from src.core.scriptgen import generate_script
from src.utils.prompt import scene_prompts
from src.core.imagegen import generate_images_from_prompts
from src.core.voice import tts_scenes
from src.core.subtitle import generate_subtitles
from src.core.assemble import assemble_video

# Import centralized configuration
from src.config import (
    validate_configuration,
    print_configuration_status,
    get_output_directories
)

@log_performance("video_generation_complete")
def main(theme, voice_provider='auto', voice_type='narrator', language=None, 
         effects_preset='professional', enable_effects=True):
    """
    Main function to generate a video from a theme.
    
    Args:
        theme (str): The theme for the video
        voice_provider (str): TTS provider ('auto', 'elevenlabs', 'gtts')
        voice_type (str): Voice type ('narrator', 'male', 'female', 'child')
        language (str): Language code (e.g., 'pt-br', 'en-us')
        effects_preset (str): Visual effects preset ('professional', 'dynamic', 'cinematic', 'energetic')
        enable_effects (bool): Whether to apply visual effects and transitions
    """
    logger = get_logger("main")
    logger.info(f"🎬 Iniciando geração de vídeo para tema: '{theme}'", extra={'extra_data': {'theme': theme, 'voice_provider': voice_provider, 'voice_type': voice_type}})
    
    # Validar configuração do sistema
    log_video_generation_step("configuration_validation", {'theme': theme})
    logger.info("🔧 Validando configuração do sistema...")
    validation = validate_configuration()
    
    if not validation['valid']:
        logger.error("❌ Configuração inválida:", extra={'extra_data': {'errors': validation['errors']}})
        for error in validation['errors']:
            logger.error(f"  - {error}")
        return False
    
    if validation['warnings']:
        logger.warning("⚠️ Avisos de configuração:", extra={'extra_data': {'warnings': validation['warnings']}})
        for warning in validation['warnings']:
            logger.warning(f"  - {warning}")
    
    # Mostrar status dos serviços
    services = validation['services_available']
    logger.info("📊 Serviços disponíveis:", extra={'extra_data': {'services_available': services}})
    if services.get('vertex_ai'):
        logger.info("  ✅ Vertex AI Imagen 3 (Principal)")
    if services.get('gemini'):
        logger.info("  ✅ Gemini 2.0 Flash (Fallback/Texto)")
    if services.get('elevenlabs'):
        logger.info("  ✅ ElevenLabs TTS")
    
    # Generate a unique ID for this video run
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_id = f"video_{theme.replace(' ', '_').lower()}_{timestamp}"
    
    # Use centralized output directories
    output_dirs = get_output_directories()
    logger.debug("Diretórios de saída configurados", extra={'extra_data': {'output_dirs': output_dirs}})
    video_output_dir = os.path.join(output_dirs['videos'], video_id)
    logger.debug("Configuração de diretórios", extra={'extra_data': {'video_output_dir': video_output_dir, 'absolute_path': os.path.abspath(video_output_dir)}})

    # Create output directories
    os.makedirs(video_output_dir, exist_ok=True)
    os.makedirs(os.path.join(video_output_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(video_output_dir, "audio"), exist_ok=True)
    os.makedirs(os.path.join(video_output_dir, "subtitles"), exist_ok=True)
    logger.info("Diretórios criados com sucesso")
    logger.info(f"Output será salvo em: {video_output_dir}")

    # Step 1: Generate structured script
    log_video_generation_step("script_generation", {'theme': theme})
    logger.info("📝 Step 1: Gerando roteiro estruturado...")
    script_data = generate_script(theme)
    if not script_data:
        logger.error("Falha na geração do roteiro. Abortando.", extra={'extra_data': {'theme': theme}})
        return False
    
    # Save the structured script
    script_path = os.path.join(video_output_dir, "script.json")
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Roteiro estruturado salvo em: {script_path}")

    # Step 2: Generate image prompts from structured script
    log_video_generation_step("image_prompts_generation")
    logger.info("🎨 Step 2: Gerando prompts de imagem...")
    prompts = scene_prompts(script_data)
    if not prompts:
        logger.error("Nenhum prompt de imagem gerado. Abortando.")
        return False
    logger.info(f"{len(prompts)} prompts extraídos do roteiro.")

    # Step 3: Generate images
    log_video_generation_step("image_generation", {'prompts_count': len(prompts)})
    logger.info("🖼️ Step 3: Gerando imagens...")
    # Pass the image output directory to imagegen
    image_output_dir = os.path.join(video_output_dir, "images")
    image_paths = generate_images_from_prompts(prompts, image_output_dir)
    if not image_paths:
        logger.error("Falha na geração de imagens. Abortando.")
        return False
    logger.info(f"{len(image_paths)} imagens geradas com sucesso.")

    # Step 4: Generate audio for each scene
    log_video_generation_step("audio_generation", {'voice_provider': voice_provider, 'voice_type': voice_type, 'language': language})
    logger.info("🎙️ Step 4: Gerando áudio...", extra={'extra_data': {'voice_provider': voice_provider, 'voice_type': voice_type, 'language': language}})
    logger.info(f"Usando provedor TTS: {voice_provider}")
    if voice_type != 'narrator':
        logger.info(f"Tipo de voz: {voice_type}")
    if language:
        logger.info(f"Idioma: {language}")
    
    # Pass the audio output directory to voice
    audio_output_dir = os.path.join(video_output_dir, "audio")
    audio_paths = tts_scenes(
        script_data, 
        audio_output_dir,
        provider=voice_provider,
        voice_type=voice_type,
        language=language
    )
    if not audio_paths:
        logger.error("Falha na geração de áudio. Abortando.")
        return False
    logger.info(f"{len(audio_paths)} arquivos de áudio gerados com sucesso.")

    # Step 5: Generate subtitles using Gemini 2.0 Flash
    log_video_generation_step("subtitle_generation")
    logger.info("📜 Step 5: Gerando legendas...")
    # Use the generated audio files to create subtitles with Gemini
    subtitle_output_dir = os.path.join(video_output_dir, "subtitles")
    subtitle_path = generate_subtitles(audio_paths, subtitle_output_dir, script_path)
    if not subtitle_path:
        logger.error("Falha na geração de legendas. Abortando.")
        return False
    logger.info(f"Legendas geradas em: {subtitle_path}")

    # Step 6: Assemble video with effects
    log_video_generation_step("video_assembly", {'effects_preset': effects_preset, 'enable_effects': enable_effects})
    logger.info("🎞️ Step 6: Montando vídeo com efeitos visuais...", extra={'extra_data': {'effects_preset': effects_preset, 'enable_effects': enable_effects}})
    # Pass all generated image and audio paths, and the final video output path
    final_video_path = os.path.join(video_output_dir, f"{video_id}.mp4")
    video_path = assemble_video(
         image_paths=image_paths, 
         audio_paths=audio_paths, 
         subtitle_path=subtitle_path, 
         final_video_path=final_video_path, 
         subtitle_style="modern",
         script_path=script_path,
         use_script_sync=True,
         effects_preset=effects_preset,
         enable_effects=enable_effects
     )
    if video_path:
        log_video_generation_step("video_completed", {'video_path': video_path, 'theme': theme})
        logger.info(f"✅ Vídeo montado com sucesso em: {video_path}")
        return True
    else:
        logger.error("❌ Falha na montagem do vídeo. Verifique os logs para erros, especialmente instalação do ffmpeg/ffprobe.")
        return False

if __name__ == "__main__":
    # Setup logging first
    setup_logging(log_dir="logs", log_level="INFO")
    parser = argparse.ArgumentParser(description="Generate a short AI comic-style video from a theme.")
    parser.add_argument("--theme", type=str, help="The theme of the video (e.g., 'Cyberpunk city exploration').")
    parser.add_argument("--test", action="store_true", help="Run in test mode using existing files (no API calls)")
    
    # Voice configuration options
    parser.add_argument("--voice-provider", type=str, default="auto", 
                       choices=["auto", "elevenlabs", "gtts"],
                       help="TTS provider to use (default: auto - prefers ElevenLabs if available)")
    parser.add_argument("--voice-type", type=str, default="narrator",
                       choices=["narrator", "male", "female", "child"],
                       help="Voice type for narration (default: narrator)")
    parser.add_argument("--language", type=str,
                       help="Language code for TTS (e.g., 'pt-br', 'en-us'). Auto-detected if not specified.")
    
    # Visual effects configuration options
    parser.add_argument("--effects-preset", type=str, default="professional",
                       choices=["professional", "dynamic", "cinematic", "subtle", "energetic"],
                       help="Visual effects preset (default: professional)")
    parser.add_argument("--no-effects", action="store_true",
                       help="Disable visual effects and transitions")
    
    args = parser.parse_args()

    # Test mode - use existing files
    if args.test:
        logger = get_logger("main")
        logger.info("🧪 Executando em modo de teste...")
        logger.info("💡 Use: python test_mode.py --list para ver projetos disponíveis")
        logger.info("💡 Use: python test_mode.py --project <nome> para testar montagem")
        sys.exit(0)
    
    # Normal mode - require theme
    if not args.theme:
        parser.error("--theme é obrigatório no modo normal. Use --test para modo de teste.")

    # Validar configuração antes de iniciar
    logger = get_logger("main")
    logger.info("🔧 Verificando configuração do sistema...")
    validation = validate_configuration()
    
    if not validation['valid']:
        logger.error("❌ Configuração inválida. Execute 'python src/config.py' para detalhes.", extra={'extra_data': {'errors': validation['errors']}})
        sys.exit(1)
    
    # Check ElevenLabs API key if specifically requested
    if args.voice_provider == "elevenlabs" and not validation['services_available'].get('elevenlabs'):
        logger.error("ELEVENLABS_API_KEY deve estar configurado para usar --voice-provider elevenlabs.")
        logger.info("Dica: Use --voice-provider auto ou gtts como alternativas.")
        sys.exit(1)
    
    # Show voice configuration info
    if args.voice_provider != "auto" or args.voice_type != "narrator" or args.language:
        logger.info("🎙️ Configuração de Voz:", extra={'extra_data': {'voice_provider': args.voice_provider, 'voice_type': args.voice_type, 'language': args.language}})
        logger.info(f"   -> Provider: {args.voice_provider}")
        logger.info(f"   -> Voice type: {args.voice_type}")
        if args.language:
            logger.info(f"   -> Language: {args.language}")
    
    # Run main function with voice and effects parameters
    main(
        args.theme,
        voice_provider=args.voice_provider,
        voice_type=args.voice_type,
        language=args.language,
        effects_preset=args.effects_preset,
        enable_effects=not args.no_effects
    )