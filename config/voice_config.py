"""Configurações de voz para diferentes provedores de TTS."""

# Configurações padrão para ElevenLabs
ELEVENLABS_DEFAULT_SETTINGS = {
    'stability': 0.5,  # Estabilidade da voz (0.0 - 1.0)
    'similarity_boost': 0.5,  # Boost de similaridade (0.0 - 1.0)
    'style': 0.0,  # Estilo da voz (0.0 - 1.0)
    'use_speaker_boost': True  # Usar boost do speaker
}

# Vozes recomendadas para ElevenLabs
ELEVENLABS_VOICES = {
    # Vozes em Português Brasileiro
    'pt-br': {
        'default': 'pNInz6obpgDQGcFmaJgB',  # Adam (voz masculina natural)
        'female': 'EXAVITQu4vr4xnSDxMaL',  # Bella (voz feminina suave)
        'male': 'pNInz6obpgDQGcFmaJgB',   # Adam (voz masculina)
        'narrator': 'VR6AewLTigWG4xSOukaG', # Sam (voz de narrador)
    },
    # Vozes em Inglês
    'en': {
        'default': 'pNInz6obpgDQGcFmaJgB',  # Adam
        'female': 'EXAVITQu4vr4xnSDxMaL',  # Bella
        'male': 'pNInz6obpgDQGcFmaJgB',   # Adam
        'narrator': 'VR6AewLTigWG4xSOukaG', # Sam
        'young_male': 'yoZ06aMxZJJ28mfd3POQ', # Antoni
        'young_female': 'AZnzlk1XvdvUeBnXmlld', # Domi
    }
}

# Mapeamento de idiomas
LANGUAGE_MAPPING = {
    'pt': 'pt-br',
    'pt-br': 'pt-br',
    'portuguese': 'pt-br',
    'en': 'en',
    'en-us': 'en',
    'english': 'en'
}

# Configurações para gTTS (fallback)
GTTS_LANGUAGES = {
    'pt-br': 'pt',
    'en': 'en'
}

def get_voice_id(language='pt-br', voice_type='default'):
    """
    Retorna o ID da voz baseado no idioma e tipo.
    
    Args:
        language (str): Idioma ('pt-br', 'en')
        voice_type (str): Tipo de voz ('default', 'male', 'female', 'narrator')
    
    Returns:
        str: ID da voz do ElevenLabs
    """
    # Normalizar idioma
    lang = LANGUAGE_MAPPING.get(language.lower(), 'pt-br')
    
    # Obter configuração de voz
    voices = ELEVENLABS_VOICES.get(lang, ELEVENLABS_VOICES['pt-br'])
    
    return voices.get(voice_type, voices['default'])

def get_gtts_language(language='pt-br'):
    """
    Retorna o código de idioma para gTTS.
    
    Args:
        language (str): Idioma
    
    Returns:
        str: Código de idioma para gTTS
    """
    lang = LANGUAGE_MAPPING.get(language.lower(), 'pt-br')
    return GTTS_LANGUAGES.get(lang, 'pt')

def detect_language_from_text(text):
    """
    Detecta o idioma do texto baseado em palavras comuns.
    
    Args:
        text (str): Texto para análise
    
    Returns:
        str: Código do idioma detectado
    """
    # Palavras comuns em português
    pt_words = ['o', 'a', 'de', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais']
    
    # Palavras comuns em inglês
    en_words = ['the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 'for', 'on', 'are', 'as', 'with', 'his', 'they', 'i']
    
    text_lower = text.lower()
    words = text_lower.split()
    
    pt_count = sum(1 for word in words if word in pt_words)
    en_count = sum(1 for word in words if word in en_words)
    
    if pt_count > en_count:
        return 'pt-br'
    else:
        return 'en'