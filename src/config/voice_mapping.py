#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Mapeamento de Vozes ElevenLabs

Este módulo mapeia nomes de personagens/vozes para IDs específicos do ElevenLabs,
permitindo identificação automática de vozes baseada no roteiro fornecido pelo usuário.

Exemplo de uso no roteiro:
    Liam (Civilian Teen) – Voice: Adam
    Spider-Man – Voice: Matthew
    Deadpool – Voice: Elliot
"""

from typing import Dict, Optional, List
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# ===== MAPEAMENTO DE VOZES ELEVENLABS =====

# Mapeamento principal: Nome da voz → ID do ElevenLabs
VOICE_MAPPING = {
    # Vozes do exemplo fornecido
    "Adam": "pNInz6obpgDQGcFmaJgB",      # Voz masculina jovem
    "Matthew": "Yko7PKHZNXotIFUBG7I9",    # Voz masculina heroica
    "Elliot": "bIHbv24MWmeRgasZH58o",     # Voz masculina cômica
    "William": "pqHfZKP75CvOlQylNhV4",    # Voz masculina séria/Batman
    "Josh": "TxGEqnHWrfWFTfGW9XjX",       # Voz masculina forte/Hulk
    
    # Vozes adicionais comuns do ElevenLabs
    "Rachel": "21m00Tcm4TlvDq8ikWAM",     # Voz feminina padrão
    "Domi": "AZnzlk1XvdvUeBnXmlld",       # Voz feminina jovem
    "Bella": "EXAVITQu4vr4xnSDxMaL",      # Voz feminina suave
    "Antoni": "ErXwobaYiN019PkySvjV",     # Voz masculina padrão
    "Elli": "MF3mGyEYCl7XYWbV9V6O",       # Voz feminina infantil
    "Sam": "yoZ06aMxZJJ28mfd3POQ",        # Voz masculina casual
    "Serena": "pMsXgVXv3BLzUgSXRplE",     # Voz feminina elegante
    "Thomas": "GBv7mTt0atIp3Br8iCZE",     # Voz masculina madura
}

# Mapeamento de aliases para facilitar uso
VOICE_ALIASES = {
    # Aliases em português
    "masculina": "Antoni",
    "feminina": "Rachel",
    "infantil": "Elli",
    "jovem": "Adam",
    "heroica": "Matthew",
    "comica": "Elliot",
    "seria": "William",
    "forte": "Josh",
    
    # Aliases em inglês
    "male": "Antoni",
    "female": "Rachel",
    "child": "Elli",
    "young": "Adam",
    "hero": "Matthew",
    "comic": "Elliot",
    "serious": "William",
    "strong": "Josh",
    
    # Aliases de personagens comuns
    "narrador": "Antoni",
    "narradora": "Rachel",
    "spiderman": "Matthew",
    "spider-man": "Matthew",
    "deadpool": "Elliot",
    "batman": "William",
    "hulk": "Josh",
}

# ===== FUNÇÕES PRINCIPAIS =====

def get_voice_id(voice_name: str) -> Optional[str]:
    """
    Obtém o ID da voz do ElevenLabs baseado no nome.
    
    Args:
        voice_name (str): Nome da voz (ex: "Adam", "Matthew")
    
    Returns:
        Optional[str]: ID da voz no ElevenLabs ou None se não encontrada
    
    Examples:
        >>> get_voice_id("Adam")
        'pNInz6obpgDQGcFmaJgB'
        
        >>> get_voice_id("masculina")
        'ErXwobaYiN019PkySvjV'
    """
    if not voice_name:
        return None
    
    # Normalizar nome (remover espaços, converter para minúsculo)
    normalized_name = voice_name.strip()
    
    # Buscar primeiro no mapeamento principal (case-sensitive)
    if normalized_name in VOICE_MAPPING:
        return VOICE_MAPPING[normalized_name]
    
    # Buscar nos aliases (case-insensitive)
    normalized_lower = normalized_name.lower()
    if normalized_lower in VOICE_ALIASES:
        alias_voice = VOICE_ALIASES[normalized_lower]
        return VOICE_MAPPING.get(alias_voice)
    
    # Log se voz não encontrada
    logger.warning(f"Voz '{voice_name}' não encontrada no mapeamento")
    return None

def get_voice_name(voice_id: str) -> Optional[str]:
    """
    Obtém o nome da voz baseado no ID do ElevenLabs.
    
    Args:
        voice_id (str): ID da voz no ElevenLabs
    
    Returns:
        Optional[str]: Nome da voz ou None se não encontrada
    """
    for name, vid in VOICE_MAPPING.items():
        if vid == voice_id:
            return name
    return None

def list_available_voices() -> List[Dict[str, str]]:
    """
    Lista todas as vozes disponíveis no mapeamento.
    
    Returns:
        List[Dict[str, str]]: Lista com informações das vozes
    """
    voices = []
    for name, voice_id in VOICE_MAPPING.items():
        voices.append({
            "name": name,
            "voice_id": voice_id,
            "type": _get_voice_type(name)
        })
    return voices

def validate_voice_exists(voice_name: str) -> bool:
    """
    Valida se uma voz existe no mapeamento.
    
    Args:
        voice_name (str): Nome da voz para validar
    
    Returns:
        bool: True se a voz existe, False caso contrário
    """
    return get_voice_id(voice_name) is not None

def get_default_voice(voice_type: str = "narrator") -> str:
    """
    Obtém uma voz padrão baseada no tipo solicitado.
    
    Args:
        voice_type (str): Tipo de voz (narrator, male, female, child)
    
    Returns:
        str: ID da voz padrão
    """
    defaults = {
        "narrator": "Antoni",
        "male": "Antoni", 
        "female": "Rachel",
        "child": "Elli"
    }
    
    voice_name = defaults.get(voice_type, "Antoni")
    return get_voice_id(voice_name) or VOICE_MAPPING["Antoni"]

# ===== FUNÇÕES AUXILIARES =====

def _get_voice_type(voice_name: str) -> str:
    """
    Determina o tipo de uma voz baseado no nome.
    
    Args:
        voice_name (str): Nome da voz
    
    Returns:
        str: Tipo da voz (male, female, child)
    """
    female_voices = ["Rachel", "Domi", "Bella", "Elli", "Serena"]
    child_voices = ["Elli"]
    
    if voice_name in child_voices:
        return "child"
    elif voice_name in female_voices:
        return "female"
    else:
        return "male"

# ===== VALIDAÇÃO DO MÓDULO =====

if __name__ == "__main__":
    # Teste básico do mapeamento
    print("🎙️ Testando Sistema de Mapeamento de Vozes")
    print("=" * 50)
    
    # Testar vozes do exemplo
    test_voices = ["Adam", "Matthew", "Elliot", "William", "Josh"]
    
    for voice in test_voices:
        voice_id = get_voice_id(voice)
        print(f"✅ {voice}: {voice_id}")
    
    # Testar aliases
    print("\n🔄 Testando Aliases:")
    aliases_test = ["masculina", "feminina", "spiderman", "batman"]
    
    for alias in aliases_test:
        voice_id = get_voice_id(alias)
        voice_name = get_voice_name(voice_id) if voice_id else None
        print(f"✅ {alias} → {voice_name} ({voice_id})")
    
    print(f"\n📊 Total de vozes mapeadas: {len(VOICE_MAPPING)}")
    print(f"📊 Total de aliases: {len(VOICE_ALIASES)}")