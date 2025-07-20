"""Sistema de legendas integrado com MoviePy.

Este módulo implementa a renderização de legendas usando MoviePy TextClip,
mantendo compatibilidade com os estilos profissionais existentes.
"""

import os
import re
from typing import List, Tuple, Optional
from moviepy import TextClip, CompositeVideoClip
from .subtitle_styles import SubtitleStyleManager, SubtitleStyle

def parse_srt_file(srt_path: str) -> List[dict]:
    """Parse de arquivo SRT para lista de legendas.
    
    Args:
        srt_path: Caminho para arquivo SRT
        
    Returns:
        Lista de dicionários com informações das legendas
    """
    if not os.path.exists(srt_path):
        return []
    
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex para extrair blocos de legenda
    pattern = r'(\d+)\s*\n([\d:,]+)\s*-->\s*([\d:,]+)\s*\n((?:.*\n?)*?)(?=\n\d+\s*\n|\Z)'
    matches = re.findall(pattern, content, re.MULTILINE)
    
    subtitles = []
    for match in matches:
        index, start_time, end_time, text = match
        
        # Converter timestamps para segundos
        start_seconds = _timestamp_to_seconds(start_time.strip())
        end_seconds = _timestamp_to_seconds(end_time.strip())
        
        # Limpar texto
        clean_text = text.strip().replace('\n', ' ')
        
        subtitles.append({
            'index': int(index),
            'start': start_seconds,
            'end': end_seconds,
            'text': clean_text,
            'duration': end_seconds - start_seconds
        })
    
    return subtitles

def _timestamp_to_seconds(timestamp: str) -> float:
    """Converte timestamp SRT para segundos.
    
    Args:
        timestamp: Timestamp no formato HH:MM:SS,mmm
        
    Returns:
        Tempo em segundos
    """
    # Formato: HH:MM:SS,mmm
    time_part, ms_part = timestamp.split(',')
    hours, minutes, seconds = map(int, time_part.split(':'))
    milliseconds = int(ms_part)
    
    total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
    return total_seconds

def create_subtitle_clips(subtitles: List[dict], style: SubtitleStyle, video_format: str = "standard") -> List[TextClip]:
    """Cria clips de texto para legendas usando MoviePy.
    
    Args:
        subtitles: Lista de legendas parseadas
        style: Configuração de estilo
        video_format: Formato do vídeo ('tiktok', 'youtube', 'standard')
        
    Returns:
        Lista de TextClips configurados
    """
    text_clips = []
    
    for subtitle in subtitles:
        # Ajustar configurações baseadas no formato
        font_size = style.font_size
        if video_format == "tiktok":
            font_size = int(style.font_size * 1.3)
        
        # Configurar posição
        position = _get_position_for_format(style, video_format)
        
        # Criar TextClip
        try:
            text_clip = TextClip(
                subtitle['text'],
                fontsize=font_size,
                font=style.font_family,
                color=style.text_color,
                stroke_color=style.outline_color if style.outline_width > 0 else None,
                stroke_width=style.outline_width if style.outline_width > 0 else 0,
                method='caption',
                size=(680, None) if video_format == "tiktok" else (1200, None),
                align='center'
            ).set_start(subtitle['start']).set_duration(subtitle['duration']).set_position(position)
            
            # Adicionar sombra se habilitada
            if style.shadow_enabled:
                # MoviePy não tem sombra nativa, mas podemos simular com stroke
                pass
            
            text_clips.append(text_clip)
            
        except Exception as e:
            print(f"Warning: Could not create text clip for subtitle '{subtitle['text']}': {e}")
            continue
    
    return text_clips

def _get_position_for_format(style: SubtitleStyle, video_format: str) -> Tuple[str, str]:
    """Determina posição das legendas baseada no formato.
    
    Args:
        style: Configuração de estilo
        video_format: Formato do vídeo
        
    Returns:
        Tupla com posição (horizontal, vertical)
    """
    if video_format == "tiktok":
        # Para TikTok (720x1280), posicionar a 30% de baixo para cima
        # 1280 * 0.3 = 384px de baixo
        return ('center', 1280 - 384)
    else:
        # Posicionamento padrão
        if style.position_v == "bottom":
            return ('center', 'bottom')
        elif style.position_v == "center":
            return ('center', 'center')
        else:  # top
            return ('center', 'top')

def apply_subtitles_to_video(video_clip, subtitle_path: str, subtitle_style: str = "modern", video_format: str = "standard"):
    """Aplica legendas a um clip de vídeo usando MoviePy.
    
    Args:
        video_clip: Clip de vídeo do MoviePy
        subtitle_path: Caminho para arquivo de legendas
        subtitle_style: Nome do estilo ou objeto SubtitleStyle
        video_format: Formato do vídeo ('tiktok', 'youtube', 'standard')
        
    Returns:
        Clip de vídeo com legendas aplicadas
    """
    if not subtitle_path or not os.path.exists(subtitle_path):
        print("Warning: Subtitle file not found, returning video without subtitles")
        return video_clip
    
    try:
        # Obter configuração de estilo
        if isinstance(subtitle_style, str):
            style_config = SubtitleStyleManager.get_style(subtitle_style)
        else:
            style_config = subtitle_style
        
        # Parse do arquivo de legendas
        subtitles = parse_srt_file(subtitle_path)
        if not subtitles:
            print("Warning: No subtitles found in file")
            return video_clip
        
        # Criar clips de texto
        text_clips = create_subtitle_clips(subtitles, style_config, video_format)
        if not text_clips:
            print("Warning: No text clips created")
            return video_clip
        
        # Compor vídeo com legendas
        final_video = CompositeVideoClip([video_clip] + text_clips)
        
        print(f"     - Subtitles applied successfully: {len(text_clips)} subtitle clips")
        return final_video
        
    except Exception as e:
        print(f"     - Error applying subtitles: {e}")
        return video_clip

def create_highlighted_subtitle_clips(subtitles: List[dict], highlighted_words: List[str], style: SubtitleStyle, video_format: str = "standard") -> List[TextClip]:
    """Cria clips de legendas com palavras destacadas.
    
    Args:
        subtitles: Lista de legendas parseadas
        highlighted_words: Lista de palavras para destacar
        style: Configuração de estilo
        video_format: Formato do vídeo
        
    Returns:
        Lista de TextClips com destaque
    """
    text_clips = []
    
    for subtitle in subtitles:
        text = subtitle['text']
        
        # Verificar se há palavras para destacar nesta legenda
        has_highlighted = any(word.lower() in text.lower() for word in highlighted_words)
        
        if has_highlighted:
            # Usar estilo destacado
            highlighted_style = SubtitleStyleManager.get_style("highlighted")
            font_size = highlighted_style.font_size
            color = "yellow"  # Cor de destaque
        else:
            # Usar estilo normal
            font_size = style.font_size
            color = style.text_color
        
        # Ajustar para formato
        if video_format == "tiktok":
            font_size = int(font_size * 1.3)
        
        position = _get_position_for_format(style, video_format)
        
        try:
            text_clip = TextClip(
                text,
                fontsize=font_size,
                font=style.font_family,
                color=color,
                stroke_color=style.outline_color if style.outline_width > 0 else None,
                stroke_width=style.outline_width if style.outline_width > 0 else 0,
                method='caption',
                size=(680, None) if video_format == "tiktok" else (1200, None),
                align='center'
            ).set_start(subtitle['start']).set_duration(subtitle['duration']).set_position(position)
            
            text_clips.append(text_clip)
            
        except Exception as e:
            print(f"Warning: Could not create highlighted text clip: {e}")
            continue
    
    return text_clips

def apply_highlighted_subtitles_to_video(video_clip, subtitle_path: str, highlighted_words: List[str], subtitle_style: str = "modern", video_format: str = "standard"):
    """Aplica legendas com palavras destacadas a um clip de vídeo.
    
    Args:
        video_clip: Clip de vídeo do MoviePy
        subtitle_path: Caminho para arquivo de legendas
        highlighted_words: Lista de palavras para destacar
        subtitle_style: Nome do estilo
        video_format: Formato do vídeo
        
    Returns:
        Clip de vídeo com legendas destacadas
    """
    if not subtitle_path or not os.path.exists(subtitle_path):
        print("Warning: Subtitle file not found")
        return video_clip
    
    try:
        # Obter configuração de estilo
        style_config = SubtitleStyleManager.get_style(subtitle_style)
        
        # Parse do arquivo de legendas
        subtitles = parse_srt_file(subtitle_path)
        if not subtitles:
            print("Warning: No subtitles found")
            return video_clip
        
        # Criar clips com destaque
        text_clips = create_highlighted_subtitle_clips(subtitles, highlighted_words, style_config, video_format)
        if not text_clips:
            print("Warning: No highlighted text clips created")
            return video_clip
        
        # Compor vídeo
        final_video = CompositeVideoClip([video_clip] + text_clips)
        
        print(f"     - Highlighted subtitles applied: {len(text_clips)} clips, {len(highlighted_words)} highlighted words")
        return final_video
        
    except Exception as e:
        print(f"     - Error applying highlighted subtitles: {e}")
        return video_clip

# Função de compatibilidade para manter interface existente
def integrate_moviepy_subtitles(video_clip, subtitle_path: str, subtitle_style: str = "modern", video_format: str = "standard", highlighted_words: Optional[List[str]] = None):
    """Função principal para integração de legendas com MoviePy.
    
    Args:
        video_clip: Clip de vídeo do MoviePy
        subtitle_path: Caminho para arquivo de legendas
        subtitle_style: Nome do estilo
        video_format: Formato do vídeo
        highlighted_words: Lista opcional de palavras para destacar
        
    Returns:
        Clip de vídeo com legendas aplicadas
    """
    if highlighted_words:
        return apply_highlighted_subtitles_to_video(
            video_clip, subtitle_path, highlighted_words, subtitle_style, video_format
        )
    else:
        return apply_subtitles_to_video(
            video_clip, subtitle_path, subtitle_style, video_format
        )