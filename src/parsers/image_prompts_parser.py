"""Parser para processar prompts de imagem organizados por cenas.

Este módulo converte prompts no formato:
Scene 1:
"Prompt da imagem para cena 1..."

Scene 2:
"Prompt da imagem para cena 2..."

Para lista de prompts estruturados.
"""

import re
from typing import List, Dict, Any, Optional


def parse_image_prompts(prompts_text: str) -> Optional[List[str]]:
    """Converte prompts de imagem organizados por cenas para lista estruturada.
    
    Args:
        prompts_text: Texto com prompts organizados por cenas
        
    Returns:
        Lista de prompts ou None se falhar
        
    Exemplo de entrada:
        Scene 1:
        "A 3D cartoon teenager standing in front of a laundry machine..."
        
        Scene 2:
        "Spider-Man clinging to the ceiling of the laundry room..."
    """
    if not prompts_text or not prompts_text.strip():
        return None
    
    try:
        # Padrões para detectar diferentes formatos de cenas
        scene_patterns = [
            r'^Scene\s+(\d+):\s*$',  # "Scene 1:"
            r'^(\d+)\.\s*$',         # "1."
            r'^-\s*Scene\s+(\d+)',   # "- Scene 1"
            r'^Cena\s+(\d+):\s*$',   # "Cena 1:"
        ]
        
        lines = prompts_text.strip().split('\n')
        prompts = []
        current_prompt = ""
        scene_number = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Verificar se é uma linha de cabeçalho de cena
            is_scene_header = False
            for pattern in scene_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    # Salvar prompt anterior se existir
                    if current_prompt.strip():
                        prompts.append(clean_prompt(current_prompt.strip()))
                    
                    # Iniciar novo prompt
                    current_prompt = ""
                    scene_number = int(match.group(1))
                    is_scene_header = True
                    break
            
            if not is_scene_header:
                # É parte do prompt da cena atual
                if current_prompt:
                    current_prompt += " " + line
                else:
                    current_prompt = line
        
        # Adicionar último prompt se existir
        if current_prompt.strip():
            prompts.append(clean_prompt(current_prompt.strip()))
        
        if not prompts:
            # Tentar parsing alternativo - texto corrido sem marcadores de cena
            return parse_prompts_fallback(prompts_text)
        
        return prompts
        
    except Exception as e:
        print(f"❌ Erro ao processar prompts de imagem: {e}")
        return None


def parse_prompts_fallback(prompts_text: str) -> Optional[List[str]]:
    """Parser alternativo para prompts sem marcadores claros de cena.
    
    Args:
        prompts_text: Texto com prompts
        
    Returns:
        Lista de prompts ou None se falhar
    """
    try:
        # Dividir por linhas e filtrar vazias
        lines = [line.strip() for line in prompts_text.strip().split('\n') if line.strip()]
        
        if not lines:
            return None
        
        # Se há apenas uma linha longa, tentar dividir por pontos ou quebras naturais
        if len(lines) == 1 and len(lines[0]) > 200:
            # Dividir por pontos seguidos de maiúscula
            sentences = re.split(r'\. (?=[A-Z])', lines[0])
            if len(sentences) > 1:
                return [clean_prompt(sentence + ('' if sentence.endswith('.') else '.')) for sentence in sentences]
        
        # Processar cada linha como um prompt
        prompts = []
        for line in lines:
            cleaned = clean_prompt(line)
            if len(cleaned) > 20:  # Filtrar prompts muito curtos
                prompts.append(cleaned)
        
        return prompts if prompts else None
        
    except Exception as e:
        print(f"❌ Erro no parser alternativo: {e}")
        return None


def clean_prompt(prompt: str) -> str:
    """Limpa e formata um prompt de imagem.
    
    Args:
        prompt: Prompt bruto
        
    Returns:
        Prompt limpo e formatado
    """
    # Remover aspas extras
    prompt = re.sub(r'^["\']|["\']$', '', prompt.strip())
    
    # Remover múltiplos espaços
    prompt = re.sub(r'\s+', ' ', prompt)
    
    # Garantir que termina com ponto
    if prompt and not prompt.endswith(('.', '!', '?')):
        prompt += '.'
    
    # Adicionar prefixo padrão se não tiver estilo definido
    style_keywords = ['3D', 'cartoon', 'realistic', 'anime', 'digital art', 'painting', 'sketch']
    has_style = any(keyword.lower() in prompt.lower() for keyword in style_keywords)
    
    if not has_style and len(prompt) > 10:
        prompt = f"A 3D cartoon style image of {prompt.lower()}"
    
    return prompt


def validate_image_prompts(prompts_text: str) -> Dict[str, Any]:
    """Valida formato dos prompts de imagem.
    
    Args:
        prompts_text: Texto com prompts a serem validados
        
    Returns:
        Dict com informações de validação
    """
    if not prompts_text or not prompts_text.strip():
        return {
            "valid": False,
            "error": "Prompts vazios",
            "prompts_found": 0,
            "total_length": 0
        }
    
    prompts = parse_image_prompts(prompts_text)
    
    if not prompts:
        return {
            "valid": False,
            "error": "Nenhum prompt válido encontrado",
            "prompts_found": 0,
            "total_length": len(prompts_text)
        }
    
    # Verificar qualidade dos prompts
    short_prompts = [p for p in prompts if len(p) < 30]
    long_prompts = [p for p in prompts if len(p) > 500]
    
    warnings = []
    if short_prompts:
        warnings.append(f"{len(short_prompts)} prompts muito curtos (< 30 chars)")
    if long_prompts:
        warnings.append(f"{len(long_prompts)} prompts muito longos (> 500 chars)")
    
    return {
        "valid": True,
        "prompts_found": len(prompts),
        "total_length": len(prompts_text),
        "average_length": sum(len(p) for p in prompts) // len(prompts),
        "warnings": warnings,
        "error": None
    }


def get_prompts_preview(prompts_text: str, max_prompts: int = 3) -> str:
    """Gera preview dos prompts processados.
    
    Args:
        prompts_text: Texto com prompts
        max_prompts: Número máximo de prompts no preview
        
    Returns:
        String com preview formatado
    """
    prompts = parse_image_prompts(prompts_text)
    if not prompts:
        return "❌ Prompts inválidos"
    
    preview_lines = []
    preview_lines.append(f"🎨 {len(prompts)} prompts de imagem detectados")
    preview_lines.append("")
    
    prompts_to_show = min(max_prompts, len(prompts))
    for i in range(prompts_to_show):
        prompt = prompts[i]
        preview_text = prompt[:100] + "..." if len(prompt) > 100 else prompt
        preview_lines.append(f"🖼️ Prompt {i+1}: {preview_text}")
        preview_lines.append("")
    
    if len(prompts) > max_prompts:
        preview_lines.append(f"... e mais {len(prompts) - max_prompts} prompts")
    
    return "\n".join(preview_lines)


def enhance_prompts_for_consistency(prompts: List[str], style_guide: str = "3D cartoon") -> List[str]:
    """Melhora prompts para consistência visual.
    
    Args:
        prompts: Lista de prompts originais
        style_guide: Guia de estilo a ser aplicado
        
    Returns:
        Lista de prompts melhorados
    """
    enhanced = []
    
    for prompt in prompts:
        # Adicionar guia de estilo se não presente
        if style_guide.lower() not in prompt.lower():
            enhanced_prompt = f"{style_guide} style, {prompt}"
        else:
            enhanced_prompt = prompt
        
        # Adicionar qualificadores de qualidade
        quality_terms = ["high quality", "detailed", "professional", "4k", "hd"]
        has_quality = any(term in enhanced_prompt.lower() for term in quality_terms)
        
        if not has_quality:
            enhanced_prompt += ", high quality, detailed"
        
        enhanced.append(enhanced_prompt)
    
    return enhanced


if __name__ == "__main__":
    # Teste do parser
    test_prompts = """Scene 1:
"A 3D cartoon teenager standing in front of a laundry machine in a modern laundry room, looking confused and startled."

Scene 2:
"Spider-Man clinging to the ceiling of the laundry room, looking down at the teenager with concern, red and blue suit clearly visible."

Scene 3:
"Close-up of the teenager's face showing worry and fear, with the laundry machine visible in the background making ominous sounds."""
    
    print("🧪 Testando parser de prompts de imagem...")
    result = parse_image_prompts(test_prompts)
    if result:
        print("✅ Prompts processados com sucesso!")
        for i, prompt in enumerate(result, 1):
            print(f"  {i}. {prompt}")
    else:
        print("❌ Falha no processamento dos prompts")
    
    print("\n📋 Preview:")
    print(get_prompts_preview(test_prompts))
    
    print("\n🔍 Validação:")
    validation = validate_image_prompts(test_prompts)
    print(f"Válido: {validation['valid']}")
    print(f"Prompts encontrados: {validation['prompts_found']}")