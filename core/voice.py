"""Generates audio from text using multiple TTS providers (gTTS, ElevenLabs), creating separate audio files for each scene's narration."""
import os
from gtts import gTTS
from typing import Optional, Dict, List

# Importar cliente ElevenLabs
try:
    from config.elevenlabs_client import ElevenLabsClient, create_elevenlabs_client
    from config.voice_config import detect_language_from_text, get_gtts_language
    ELEVENLABS_AVAILABLE = True
except ImportError as e:
    print(f"ElevenLabs não disponível: {e}")
    ELEVENLABS_AVAILABLE = False

def tts_scenes(
    script_data, 
    output_dir, 
    provider: str = 'auto',
    voice_type: str = 'default',
    voice_id: Optional[str] = None,
    language: Optional[str] = None,
    elevenlabs_settings: Optional[Dict] = None
):
    """
    Generates audio for each scene's narration using multiple TTS providers.

    Args:
        script_data: A dictionary representing the structured script.
        output_dir: The directory where audio files will be saved.
        provider (str): TTS provider ('elevenlabs', 'gtts', 'auto')
        voice_type (str): Type of voice ('default', 'male', 'female', 'narrator')
        voice_id (str, optional): Specific voice ID for ElevenLabs
        language (str, optional): Language code (auto-detected if not provided)
        elevenlabs_settings (dict, optional): Custom ElevenLabs settings

    Returns:
        A list of paths to the generated audio files, one for each scene.
    """
    audio_paths = []

    if not isinstance(script_data, dict) or "scenes" not in script_data:
        print("Error: Invalid script format. Expected a dictionary with a 'scenes' key.")
        return []

    # Determinar provedor a usar
    selected_provider = _select_provider(provider)
    print(f"🎙️ Usando provedor de TTS: {selected_provider.upper()}")
    
    # Inicializar cliente ElevenLabs se necessário
    elevenlabs_client = None
    if selected_provider == 'elevenlabs':
        elevenlabs_client = create_elevenlabs_client()
        if not elevenlabs_client or not elevenlabs_client.is_available():
            print("⚠️ ElevenLabs não disponível, usando gTTS como fallback")
            selected_provider = 'gtts'

    for i, scene in enumerate(script_data["scenes"]):
        narration_text = scene.get("narration")
        if not narration_text:
            print(f"Warning: Scene {scene.get('scene', '?')} is missing narration text. Skipping audio generation for this scene.")
            continue

        audio_path = os.path.join(output_dir, f"audio_scene_{i+1:02d}.mp3")
        print(f"  -> Generating audio for scene {i+1}: '{narration_text[:50]}...' ")

        success = False
        
        # Tentar gerar áudio com o provedor selecionado
        if selected_provider == 'elevenlabs' and elevenlabs_client:
            success = _generate_elevenlabs_audio(
                elevenlabs_client,
                narration_text,
                audio_path,
                voice_id=voice_id,
                language=language,
                voice_type=voice_type,
                settings=elevenlabs_settings
            )
        
        # Fallback para gTTS se ElevenLabs falhar
        if not success:
            if selected_provider == 'elevenlabs':
                print("     - Fallback para gTTS")
            success = _generate_gtts_audio(narration_text, audio_path, language)
        
        if success:
            audio_paths.append(audio_path)
        else:
            print(f"     - Falha ao gerar áudio para cena {i+1}")

    return audio_paths

def _select_provider(provider: str) -> str:
    """
    Seleciona o provedor de TTS baseado na preferência e disponibilidade.
    
    Args:
        provider (str): Provedor preferido ('elevenlabs', 'gtts', 'auto')
    
    Returns:
        str: Provedor selecionado
    """
    if provider == 'auto':
        # Auto: preferir ElevenLabs se disponível, senão gTTS
        if ELEVENLABS_AVAILABLE and os.getenv('ELEVENLABS_API_KEY'):
            return 'elevenlabs'
        else:
            return 'gtts'
    elif provider == 'elevenlabs':
        if not ELEVENLABS_AVAILABLE:
            print("⚠️ ElevenLabs não está instalado, usando gTTS")
            return 'gtts'
        elif not os.getenv('ELEVENLABS_API_KEY'):
            print("⚠️ ELEVENLABS_API_KEY não configurada, usando gTTS")
            return 'gtts'
        return 'elevenlabs'
    else:
        return 'gtts'

def _generate_elevenlabs_audio(
    client: 'ElevenLabsClient',
    text: str,
    output_path: str,
    voice_id: Optional[str] = None,
    language: Optional[str] = None,
    voice_type: str = 'default',
    settings: Optional[Dict] = None
) -> bool:
    """
    Gera áudio usando ElevenLabs.
    
    Args:
        client: Cliente ElevenLabs
        text: Texto para converter
        output_path: Caminho do arquivo de saída
        voice_id: ID específico da voz
        language: Idioma
        voice_type: Tipo de voz
        settings: Configurações customizadas
    
    Returns:
        bool: True se sucesso, False caso contrário
    """
    try:
        return client.save_audio(
            text=text,
            output_path=output_path,
            voice_id=voice_id,
            language=language,
            voice_type=voice_type,
            settings=settings
        )
    except Exception as e:
        print(f"     - Erro ElevenLabs: {e}")
        return False

def _generate_gtts_audio(
    text: str,
    output_path: str,
    language: Optional[str] = None
) -> bool:
    """
    Gera áudio usando gTTS.
    
    Args:
        text: Texto para converter
        output_path: Caminho do arquivo de saída
        language: Idioma (opcional)
    
    Returns:
        bool: True se sucesso, False caso contrário
    """
    try:
        # Detectar idioma se não fornecido
        if not language:
            if ELEVENLABS_AVAILABLE:
                detected_lang = detect_language_from_text(text)
                gtts_lang = get_gtts_language(detected_lang)
            else:
                # Fallback simples se config não disponível
                gtts_lang = 'pt' if any(word in text.lower() for word in ['o', 'a', 'de', 'que', 'e']) else 'en'
        else:
            if ELEVENLABS_AVAILABLE:
                gtts_lang = get_gtts_language(language)
            else:
                gtts_lang = 'pt' if language.startswith('pt') else 'en'
        
        tts = gTTS(text=text, lang=gtts_lang)
        tts.save(output_path)
        print(f"     - Áudio gTTS salvo em: {output_path}")
        return True
        
    except Exception as e:
        print(f"     - Erro gTTS: {e}")
        return False

# Funções de conveniência para compatibilidade
def tts_scenes_gtts(script_data, output_dir, language='auto'):
    """
    Função de compatibilidade para gerar áudio apenas com gTTS.
    
    Args:
        script_data: Dados do script
        output_dir: Diretório de saída
        language: Idioma ('auto', 'pt', 'en')
    
    Returns:
        Lista de caminhos dos arquivos de áudio
    """
    return tts_scenes(
        script_data=script_data,
        output_dir=output_dir,
        provider='gtts',
        language=language
    )

def tts_scenes_elevenlabs(
    script_data,
    output_dir,
    voice_type='default',
    voice_id=None,
    language='auto',
    settings=None
):
    """
    Função de conveniência para gerar áudio apenas com ElevenLabs.
    
    Args:
        script_data: Dados do script
        output_dir: Diretório de saída
        voice_type: Tipo de voz
        voice_id: ID específico da voz
        language: Idioma
        settings: Configurações customizadas
    
    Returns:
        Lista de caminhos dos arquivos de áudio
    """
    return tts_scenes(
        script_data=script_data,
        output_dir=output_dir,
        provider='elevenlabs',
        voice_type=voice_type,
        voice_id=voice_id,
        language=language,
        elevenlabs_settings=settings
    )

if __name__ == '__main__':
    # Example usage for testing
    test_script = {
      "theme": "The secret life of garden gnomes",
      "title": "Gnome Sweet Gnome",
      "scenes": [
        {
          "scene": 1,
          "visual_description": "digital comic book art of a garden gnome secretly polishing his fishing rod at midnight, with the moon shining brightly.",
          "narration": "At night, the garden reveals its secrets."
        },
        {
          "scene": 2,
          "visual_description": "digital comic book art of two gnomes playing a high-stakes game of poker on a toadstool table.",
          "narration": "Bernard was all in, but Gerald held the winning hand."
        }
      ]
    }
    
    # Script em português para teste
    test_script_pt = {
      "theme": "A vida secreta dos gnomos de jardim",
      "title": "Gnomo Doce Lar",
      "scenes": [
        {
          "scene": 1,
          "visual_description": "arte de quadrinhos digitais de um gnomo de jardim secretamente polindo sua vara de pescar à meia-noite, com a lua brilhando intensamente.",
          "narration": "À noite, o jardim revela seus segredos."
        },
        {
          "scene": 2,
          "visual_description": "arte de quadrinhos digitais de dois gnomos jogando um jogo de pôquer de alto risco em uma mesa de cogumelo.",
          "narration": "Bernardo estava all-in, mas Geraldo tinha a mão vencedora."
        }
      ]
    }
    
    # For testing, create a dummy output directory
    test_output_dir = "test_output_audio"
    os.makedirs(test_output_dir, exist_ok=True)
    
    print("🎙️ Testando sistema de TTS multi-provedor")
    print("="*50)
    
    # Teste 1: Auto (preferir ElevenLabs se disponível)
    print("\n📋 Teste 1: Provedor automático")
    generated_audio_paths = tts_scenes(
        test_script_pt, 
        test_output_dir,
        provider='auto',
        voice_type='narrator'
    )
    
    # Teste 2: Forçar gTTS
    print("\n📋 Teste 2: Forçar gTTS")
    gtts_paths = tts_scenes(
        test_script, 
        test_output_dir,
        provider='gtts'
    )
    
    # Teste 3: Tentar ElevenLabs (se disponível)
    if ELEVENLABS_AVAILABLE and os.getenv('ELEVENLABS_API_KEY'):
        print("\n📋 Teste 3: ElevenLabs")
        elevenlabs_paths = tts_scenes(
            test_script_pt,
            test_output_dir,
            provider='elevenlabs',
            voice_type='female',
            language='pt-br'
        )
    else:
        print("\n📋 Teste 3: ElevenLabs não disponível (API key não configurada)")
    
    print("\n--- Arquivos de Áudio Gerados ---")
    all_files = [f for f in os.listdir(test_output_dir) if f.endswith('.mp3')]
    for f in sorted(all_files):
        print(f"- {os.path.join(test_output_dir, f)}")
    print("--------------------------------")
    
    # Informações sobre configuração
    print("\n🔧 Informações de Configuração:")
    print(f"- ElevenLabs disponível: {ELEVENLABS_AVAILABLE}")
    print(f"- API Key configurada: {'Sim' if os.getenv('ELEVENLABS_API_KEY') else 'Não'}")
    print(f"- Provedor padrão: {_select_provider('auto')}")