"""Configuração principal do sistema AI Video GPT.

Este módulo centraliza todas as configurações do sistema, incluindo
modelos de IA, APIs e configurações de geração de conteúdo.
"""

import os
from typing import Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ============================================================================
# CONFIGURAÇÕES DE MODELOS DE IA
# ============================================================================

# Configuração de geração de imagens
IMAGE_GENERATION_CONFIG = {
    # Modelo principal: Vertex AI Imagen 3
    'primary_model': 'vertex_ai',
    'fallback_model': 'gemini',
    
    # Configurações do Vertex AI
    'vertex_ai': {
        'project_id': os.getenv('GOOGLE_CLOUD_PROJECT'),
        'location': 'us-central1',
        'model_name': 'imagen-3.0-generate-001',
        'default_aspect_ratio': '1:1',
        'default_safety_filter': 'block_some',
        'default_person_generation': 'allow_adult'
    },
    
    # Configurações do Gemini (fallback)
    'gemini': {
        'api_key': os.getenv('GEMINI_API_KEY'),
        'model_name': 'gemini-2.0-flash-exp',
        'include_text_response': False
    }
}

# Configuração de geração de texto/script
TEXT_GENERATION_CONFIG = {
    'model': 'gemini-2.0-flash-exp',
    'api_key': os.getenv('GEMINI_API_KEY'),
    'max_tokens': 2048,
    'temperature': 0.7
}

# Configuração de síntese de voz
VOICE_SYNTHESIS_CONFIG = {
    'provider': 'elevenlabs',
    'api_key': os.getenv('ELEVENLABS_API_KEY'),
    'default_voice': 'pt-br-male-1',
    'default_settings': {
        'stability': 0.5,
        'similarity_boost': 0.5,
        'style': 0.0,
        'use_speaker_boost': True
    }
}

# ============================================================================
# CONFIGURAÇÕES DE SISTEMA
# ============================================================================

# Diretórios de saída
OUTPUT_DIRECTORIES = {
    'base': 'outputs',
    'videos': 'outputs/videos',
    'images': 'outputs/images',
    'audio': 'outputs/audio',
    'subtitles': 'outputs/subtitles',
    'scripts': 'outputs/scripts',
    'reports': 'outputs/reports'
}

# Configurações de vídeo
VIDEO_CONFIG = {
    'default_fps': 24,
    'default_duration_per_scene': 5,
    'default_resolution': (1920, 1080),
    'default_format': 'mp4',
    'default_codec': 'libx264'
}

# Configurações de custo
COST_CONFIG = {
    'track_costs': True,
    'currency': 'USD',
    'rates': {
        'vertex_ai_image_generation': 0.02,  # Por imagem
        'gemini_image_generation': 0.01,     # Por imagem
        'gemini_text_generation': 0.001,     # Por 1K tokens
        'elevenlabs_tts': 0.18               # Por 1K caracteres
    }
}

# ============================================================================
# FUNÇÕES DE CONFIGURAÇÃO
# ============================================================================

def get_image_generation_config() -> Dict[str, Any]:
    """Retorna configuração de geração de imagens."""
    return IMAGE_GENERATION_CONFIG.copy()

def get_text_generation_config() -> Dict[str, Any]:
    """Retorna configuração de geração de texto."""
    return TEXT_GENERATION_CONFIG.copy()

def get_voice_synthesis_config() -> Dict[str, Any]:
    """Retorna configuração de síntese de voz."""
    return VOICE_SYNTHESIS_CONFIG.copy()

def get_output_directories() -> Dict[str, str]:
    """Retorna diretórios de saída."""
    return OUTPUT_DIRECTORIES.copy()

def get_video_config() -> Dict[str, Any]:
    """Retorna configuração de vídeo."""
    return VIDEO_CONFIG.copy()

def get_cost_config() -> Dict[str, Any]:
    """Retorna configuração de custos."""
    return COST_CONFIG.copy()

def validate_configuration() -> Dict[str, Any]:
    """Valida a configuração do sistema.
    
    Returns:
        Dict contendo status da validação e detalhes.
    """
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'services_available': {}
    }
    
    # Verificar Vertex AI
    vertex_ai_available = bool(IMAGE_GENERATION_CONFIG['vertex_ai']['project_id'])
    validation_result['services_available']['vertex_ai'] = vertex_ai_available
    
    if not vertex_ai_available:
        validation_result['warnings'].append(
            'GOOGLE_CLOUD_PROJECT não configurado - Vertex AI indisponível'
        )
    
    # Verificar Gemini
    gemini_available = bool(IMAGE_GENERATION_CONFIG['gemini']['api_key'])
    validation_result['services_available']['gemini'] = gemini_available
    
    if not gemini_available:
        validation_result['warnings'].append(
            'GEMINI_API_KEY não configurado - Gemini indisponível'
        )
    
    # Verificar se pelo menos um serviço de imagem está disponível
    if not vertex_ai_available and not gemini_available:
        validation_result['valid'] = False
        validation_result['errors'].append(
            'Nenhum serviço de geração de imagens configurado'
        )
    
    # Verificar ElevenLabs
    elevenlabs_available = bool(VOICE_SYNTHESIS_CONFIG['api_key'])
    validation_result['services_available']['elevenlabs'] = elevenlabs_available
    
    if not elevenlabs_available:
        validation_result['warnings'].append(
            'ELEVENLABS_API_KEY não configurado - Síntese de voz indisponível'
        )
    
    # Verificar geração de texto
    text_generation_available = bool(TEXT_GENERATION_CONFIG['api_key'])
    validation_result['services_available']['text_generation'] = text_generation_available
    
    if not text_generation_available:
        validation_result['valid'] = False
        validation_result['errors'].append(
            'GEMINI_API_KEY não configurado - Geração de texto indisponível'
        )
    
    return validation_result

def print_configuration_status():
    """Imprime o status da configuração do sistema."""
    print("🔧 STATUS DA CONFIGURAÇÃO DO SISTEMA")
    print("=" * 50)
    
    validation = validate_configuration()
    
    # Status geral
    if validation['valid']:
        print("✅ Configuração válida")
    else:
        print("❌ Configuração inválida")
    
    print()
    
    # Serviços disponíveis
    print("📊 SERVIÇOS DISPONÍVEIS:")
    services = validation['services_available']
    
    # Geração de imagens
    print(f"  🎨 Geração de Imagens:")
    if services.get('vertex_ai'):
        print(f"    ✅ Vertex AI Imagen 3 (Principal)")
    else:
        print(f"    ❌ Vertex AI Imagen 3")
    
    if services.get('gemini'):
        print(f"    ✅ Gemini 2.0 Flash (Fallback)")
    else:
        print(f"    ❌ Gemini 2.0 Flash")
    
    # Outros serviços
    print(f"  📝 Geração de Texto: {'✅' if services.get('text_generation') else '❌'}")
    print(f"  🎤 Síntese de Voz: {'✅' if services.get('elevenlabs') else '❌'}")
    
    # Erros e avisos
    if validation['errors']:
        print("\n❌ ERROS:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    if validation['warnings']:
        print("\n⚠️ AVISOS:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    print()

if __name__ == "__main__":
    print_configuration_status()