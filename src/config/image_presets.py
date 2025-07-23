"""Presets de estilo visual para geração de imagens.

Este módulo define diferentes presets de estilo que podem ser aplicados
na geração de imagens para garantir consistência visual e qualidade.

Autor: AI Video GPT
Data: 2024
"""

from typing import Dict, Any, List

# ============================================================================
# DEFINIÇÕES DE PRESETS DE IMAGEM
# ============================================================================

IMAGE_STYLE_PRESETS = {
    '3d_cartoon': {
        'name': '3D Cartoon (Pixar/Fortnite)',
        'description': 'Estilo 3D cartoon com visual estilizado que combina Pixar e Fortnite',
        'base_prompt': (
            "3D cartoon style with stylized visual that combines Pixar charm with Fortnite energy. "
            "Characters with rounded features, exaggerated proportions and well-defined silhouettes. "
            "Vivid colors and clean outlines. Vertical format (9:16), perfect for videos and social media."
        ),
        'environment': (
            "Modern residential building interior with interconnected environments "
            "(elevator, hallway, staircase, living room, kitchen, balcony). "
            "Consistent details like same floor pattern, doors, lighting and wall design, "
            "reinforcing continuity between scenes."
        ),
        'lighting': (
            "Soft and well-distributed light with cartoonish shadows and exaggerated shine "
            "on metallic surfaces (door handles, appliances, elevator details). "
            "Indoor lighting style with warm artificial or diffuse light."
        ),
        'color_palette': (
            "Vibrant and saturated palette with predominance of purple, red and blue tones "
            "in background elements, clothes and objects. Harmonious tones with well-defined contrasts."
        ),
        'characters': (
            "Stylized appearance with expressive face, large eyes and cartoonish facial features. "
            "Exaggerated and colorful clothes with visual elements that reinforce personality "
            "(large backpacks, caps, flashy boots, bright accessories). "
            "Dynamic and theatrical poses, always with suggested movement, even in static images. "
            "Style and trait consistency must be maintained in all character appearances."
        ),
        'expressions': (
            "Always well-marked facial expressions with clear emotions "
            "(joy, fear, surprise, determination, etc.) that match the scene narrative. "
            "Body language should reinforce these emotions."
        ),
        'technical_specs': {
            'aspect_ratio': '9:16',
            'quality_terms': ['high quality', 'detailed', '4k', 'professional rendering'],
            'consistency_terms': [
                'uniform modeling style',
                'consistent lighting and texture',
                'avoid abrupt variations in character or object design',
                'scenes should convey continuity feeling',
                'like frames from the same animation'
            ]
        }
    },
    
    'realistic': {
        'name': 'Realístico',
        'description': 'Estilo fotorrealístico com alta qualidade e detalhamento',
        'base_prompt': (
            "Photorealistic style with high quality and detailed rendering. "
            "Professional photography lighting and composition."
        ),
        'environment': 'Realistic environments with natural lighting and authentic details.',
        'lighting': 'Natural or professional studio lighting with realistic shadows and highlights.',
        'color_palette': 'Natural color palette with realistic saturation and contrast.',
        'characters': 'Realistic human proportions and features with natural expressions.',
        'expressions': 'Natural and subtle facial expressions that convey genuine emotions.',
        'technical_specs': {
            'aspect_ratio': '16:9',
            'quality_terms': ['photorealistic', '8k', 'ultra detailed', 'professional photography'],
            'consistency_terms': ['consistent lighting', 'uniform style', 'realistic proportions']
        }
    },
    
    'anime': {
        'name': 'Anime',
        'description': 'Estilo anime japonês com características típicas do gênero',
        'base_prompt': (
            "Anime style with typical Japanese animation characteristics. "
            "Large expressive eyes, stylized hair and dynamic poses."
        ),
        'environment': 'Anime-style environments with vibrant colors and stylized architecture.',
        'lighting': 'Dramatic anime lighting with strong contrasts and cel-shading effects.',
        'color_palette': 'Vibrant anime color palette with saturated colors and strong contrasts.',
        'characters': 'Anime character design with large eyes, stylized hair and expressive features.',
        'expressions': 'Exaggerated anime expressions with clear emotional communication.',
        'technical_specs': {
            'aspect_ratio': '16:9',
            'quality_terms': ['anime style', 'cel-shaded', 'vibrant colors', 'detailed'],
            'consistency_terms': ['consistent anime style', 'uniform character design', 'cel-shading']
        }
    },
    
    'digital_art': {
        'name': 'Arte Digital',
        'description': 'Estilo de arte digital moderna com efeitos visuais avançados',
        'base_prompt': (
            "Modern digital art style with advanced visual effects and artistic rendering. "
            "Creative use of colors, lighting and digital techniques."
        ),
        'environment': 'Artistic digital environments with creative lighting and effects.',
        'lighting': 'Artistic lighting with creative use of colors and digital effects.',
        'color_palette': 'Creative color palette with artistic color combinations and gradients.',
        'characters': 'Stylized digital art character design with artistic interpretation.',
        'expressions': 'Artistic interpretation of emotions with creative visual elements.',
        'technical_specs': {
            'aspect_ratio': '1:1',
            'quality_terms': ['digital art', 'artistic', 'creative', 'high resolution'],
            'consistency_terms': ['consistent art style', 'uniform digital technique', 'artistic coherence']
        }
    }
}

# ============================================================================
# FUNÇÕES DE UTILIDADE
# ============================================================================

def get_available_presets() -> List[str]:
    """Retorna lista de presets de imagem disponíveis."""
    return list(IMAGE_STYLE_PRESETS.keys())

def get_preset_info(preset: str) -> Dict[str, Any]:
    """Retorna informações sobre um preset específico."""
    return IMAGE_STYLE_PRESETS.get(preset, {})

def get_preset_names() -> Dict[str, str]:
    """Retorna dicionário com nomes amigáveis dos presets."""
    return {key: value['name'] for key, value in IMAGE_STYLE_PRESETS.items()}

def build_enhanced_prompt(base_prompt: str, preset: str = '3d_cartoon') -> str:
    """Constrói um prompt melhorado aplicando um preset específico.
    
    Args:
        base_prompt: Prompt base da cena
        preset: Nome do preset a ser aplicado
        
    Returns:
        Prompt melhorado com o estilo do preset aplicado
    """
    if preset not in IMAGE_STYLE_PRESETS:
        return base_prompt
    
    preset_config = IMAGE_STYLE_PRESETS[preset]
    
    # Construir prompt melhorado
    enhanced_parts = []
    
    # Adicionar estilo base
    enhanced_parts.append(preset_config['base_prompt'])
    
    # Adicionar prompt da cena
    enhanced_parts.append(base_prompt)
    
    # Adicionar especificações do ambiente
    enhanced_parts.append(preset_config['environment'])
    
    # Adicionar especificações de iluminação
    enhanced_parts.append(preset_config['lighting'])
    
    # Adicionar paleta de cores
    enhanced_parts.append(preset_config['color_palette'])
    
    # Adicionar especificações de personagens
    enhanced_parts.append(preset_config['characters'])
    
    # Adicionar especificações de expressões
    enhanced_parts.append(preset_config['expressions'])
    
    # Adicionar termos de qualidade
    quality_terms = ', '.join(preset_config['technical_specs']['quality_terms'])
    enhanced_parts.append(quality_terms)
    
    # Adicionar termos de consistência
    consistency_terms = ', '.join(preset_config['technical_specs']['consistency_terms'])
    enhanced_parts.append(consistency_terms)
    
    # Juntar todas as partes
    enhanced_prompt = '. '.join(enhanced_parts)
    
    return enhanced_prompt

def apply_preset_to_prompts(prompts: List[str], preset: str = '3d_cartoon') -> List[str]:
    """Aplica um preset a uma lista de prompts.
    
    Args:
        prompts: Lista de prompts originais
        preset: Nome do preset a ser aplicado
        
    Returns:
        Lista de prompts com o preset aplicado
    """
    if preset not in IMAGE_STYLE_PRESETS:
        return prompts
    
    enhanced_prompts = []
    for prompt in prompts:
        enhanced_prompt = build_enhanced_prompt(prompt, preset)
        enhanced_prompts.append(enhanced_prompt)
    
    return enhanced_prompts

def get_preset_aspect_ratio(preset: str) -> str:
    """Retorna a proporção de aspecto recomendada para um preset.
    
    Args:
        preset: Nome do preset
        
    Returns:
        String com a proporção de aspecto (ex: '9:16', '16:9', '1:1')
    """
    if preset in IMAGE_STYLE_PRESETS:
        return IMAGE_STYLE_PRESETS[preset]['technical_specs']['aspect_ratio']
    return '1:1'  # Padrão

def validate_preset(preset: str) -> bool:
    """Valida se um preset existe.
    
    Args:
        preset: Nome do preset a ser validado
        
    Returns:
        True se o preset existe, False caso contrário
    """
    return preset in IMAGE_STYLE_PRESETS

# ============================================================================
# FUNÇÃO DE TESTE
# ============================================================================

def test_presets():
    """Testa os presets de imagem."""
    print("🎨 Testando Presets de Imagem")
    print("=" * 50)
    
    # Listar presets disponíveis
    presets = get_available_presets()
    print(f"📋 Presets disponíveis: {len(presets)}")
    
    for preset in presets:
        info = get_preset_info(preset)
        print(f"\n🖼️ {preset.upper()}:")
        print(f"   Nome: {info['name']}")
        print(f"   Descrição: {info['description']}")
        print(f"   Proporção: {info['technical_specs']['aspect_ratio']}")
    
    # Testar aplicação de preset
    print("\n🧪 Testando aplicação do preset '3d_cartoon':")
    test_prompt = "A teenager looking confused in a laundry room"
    enhanced = build_enhanced_prompt(test_prompt, '3d_cartoon')
    print(f"\nPrompt original: {test_prompt}")
    print(f"\nPrompt melhorado: {enhanced[:200]}...")
    
    print("\n✅ Teste concluído com sucesso!")

if __name__ == "__main__":
    test_presets()