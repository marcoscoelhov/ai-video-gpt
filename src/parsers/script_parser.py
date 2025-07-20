"""Parser para processar roteiros personalizados com personagens e vozes.

Este módulo converte roteiros no formato:
Personagem (Descrição) – Voice: VoiceID
Texto da fala...

Para o formato JSON estruturado esperado pelo sistema.
"""

import re
import json
from typing import List, Dict, Any, Optional
from src.config.voice_mapping import get_voice_id, list_available_voices


def parse_custom_script(script_text: str) -> Optional[Dict[str, Any]]:
    """Converte roteiro personalizado para formato JSON estruturado.
    
    Args:
        script_text: Texto do roteiro no formato personalizado
        
    Returns:
        Dict com estrutura de script ou None se falhar
        
    Exemplo de entrada:
        Liam (Civilian Teen) – Voice: Adam
        My laundry machine just screamed at me.
        
        Spider-Man – Voice: Matthew
        That's bad. Did it sound like a scream-scream?
    """
    if not script_text or not script_text.strip():
        return None
    
    try:
        # Padrão para detectar linhas de personagem com voz (aceita - ou –)
        character_pattern = r'^(.+?)(?:\s*\([^)]*\))?\s*[–-]\s*Voice:\s*(.+?)$'
        
        lines = script_text.strip().split('\n')
        scenes = []
        current_scene = None
        scene_number = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Verificar se é uma linha de personagem
            character_match = re.match(character_pattern, line, re.IGNORECASE)
            
            if character_match:
                # Salvar cena anterior se existir
                if current_scene and current_scene.get('narration'):
                    scenes.append(current_scene)
                
                # Extrair informações do personagem
                character_name = character_match.group(1).strip()
                voice_name = character_match.group(2).strip()
                
                # Obter ID da voz
                voice_id = get_voice_id(voice_name)
                if not voice_id:
                    print(f"⚠️ Voz '{voice_name}' não encontrada. Usando voz padrão.")
                    voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam como padrão
                
                # Criar nova cena
                current_scene = {
                    "scene_number": scene_number,
                    "character": character_name,
                    "voice_id": voice_id,
                    "voice_name": voice_name,
                    "narration": "",
                    "visual_description": f"Cena {scene_number} com {character_name}"
                }
                scene_number += 1
                
            else:
                # É uma linha de diálogo
                if current_scene is not None:
                    if current_scene["narration"]:
                        current_scene["narration"] += " " + line
                    else:
                        current_scene["narration"] = line
        
        # Adicionar última cena se existir
        if current_scene and current_scene.get('narration'):
            scenes.append(current_scene)
        
        if not scenes:
            return None
        
        # Criar estrutura final
        script_data = {
            "title": "Roteiro Personalizado",
            "description": "Roteiro fornecido pelo usuário com personagens e vozes personalizadas",
            "total_scenes": len(scenes),
            "estimated_duration": estimate_duration(scenes),
            "scenes": scenes,
            "metadata": {
                "created_from": "custom_script",
                "total_characters": len(set(scene["character"] for scene in scenes)),
                "voices_used": list(set(scene["voice_name"] for scene in scenes))
            }
        }
        
        return script_data
        
    except Exception as e:
        print(f"❌ Erro ao processar script: {e}")
        return None


def estimate_duration(scenes: List[Dict]) -> int:
    """Estima duração total do vídeo baseado no texto.
    
    Args:
        scenes: Lista de cenas com narração
        
    Returns:
        Duração estimada em segundos
    """
    total_words = 0
    for scene in scenes:
        words = len(scene.get('narration', '').split())
        total_words += words
    
    # Estimativa: ~150 palavras por minuto
    duration_minutes = total_words / 150
    return max(30, int(duration_minutes * 60))  # Mínimo 30 segundos


def validate_script_format(script_text: str) -> Dict[str, Any]:
    """Valida formato do script e retorna informações de validação.
    
    Args:
        script_text: Texto do script a ser validado
        
    Returns:
        Dict com informações de validação
    """
    if not script_text or not script_text.strip():
        return {
            "valid": False,
            "error": "Script vazio",
            "scenes_found": 0,
            "characters_found": 0
        }
    
    character_pattern = r'^(.+?)(?:\s*\([^)]*\))?\s*[–-]\s*Voice:\s*(.+?)$'
    lines = script_text.strip().split('\n')
    
    scenes_found = 0
    characters = set()
    invalid_voices = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        character_match = re.match(character_pattern, line, re.IGNORECASE)
        if character_match:
            scenes_found += 1
            character_name = character_match.group(1).strip()
            voice_name = character_match.group(2).strip()
            
            characters.add(character_name)
            
            # Verificar se a voz existe
            if not get_voice_id(voice_name):
                invalid_voices.append(voice_name)
    
    return {
        "valid": scenes_found > 0,
        "scenes_found": scenes_found,
        "characters_found": len(characters),
        "invalid_voices": invalid_voices,
        "error": None if scenes_found > 0 else "Nenhuma cena válida encontrada"
    }


def get_script_preview(script_text: str, max_scenes: int = 3) -> str:
    """Gera preview do script processado.
    
    Args:
        script_text: Texto do script
        max_scenes: Número máximo de cenas no preview
        
    Returns:
        String com preview formatado
    """
    script_data = parse_custom_script(script_text)
    if not script_data:
        return "❌ Script inválido"
    
    preview_lines = []
    preview_lines.append(f"📋 {script_data['title']}")
    preview_lines.append(f"🎬 {script_data['total_scenes']} cenas • ⏱️ ~{script_data['estimated_duration']}s")
    preview_lines.append("")
    
    scenes_to_show = min(max_scenes, len(script_data['scenes']))
    for i in range(scenes_to_show):
        scene = script_data['scenes'][i]
        preview_lines.append(f"🎭 Cena {scene['scene_number']}: {scene['character']} ({scene['voice_name']})")
        preview_text = scene['narration'][:100] + "..." if len(scene['narration']) > 100 else scene['narration']
        preview_lines.append(f"💬 {preview_text}")
        preview_lines.append("")
    
    if script_data['total_scenes'] > max_scenes:
        preview_lines.append(f"... e mais {script_data['total_scenes'] - max_scenes} cenas")
    
    return "\n".join(preview_lines)


if __name__ == "__main__":
    # Teste do parser
    test_script = """Liam (Civilian Teen) – Voice: Adam
My laundry machine just screamed at me.

Spider-Man – Voice: Matthew
That's bad. Did it sound like a scream-scream?

Liam (Civilian Teen) – Voice: Adam
No, it sounded like a help-me-I'm-dying scream."""
    
    print("🧪 Testando parser de script...")
    result = parse_custom_script(test_script)
    if result:
        print("✅ Script processado com sucesso!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("❌ Falha no processamento do script")
    
    print("\n📋 Preview:")
    print(get_script_preview(test_script))