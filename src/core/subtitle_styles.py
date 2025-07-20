"""Sistema de estilização avançada para legendas.

Este módulo implementa estilos modernos e profissionais para legendas,
baseado nas melhores práticas da indústria.
"""

import os
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class SubtitleStyle:
    """Configurações de estilo para legendas."""
    
    # Configurações de fonte
    font_family: str = "Arial"
    font_size: int = 22
    font_weight: str = "bold"
    
    # Configurações de cor
    text_color: str = "white"
    background_color: str = "black"
    background_opacity: float = 0.8
    outline_color: str = "black"
    outline_width: int = 2
    
    # Configurações de posicionamento
    position_v: str = "bottom"  # top, center, bottom
    position_h: str = "center"  # left, center, right
    margin_bottom: int = 50
    margin_horizontal: int = 20
    
    # Configurações de formatação
    max_chars_per_line: int = 42
    max_lines: int = 2
    line_spacing: float = 1.2
    
    # Configurações de timing
    chars_per_second: int = 21
    min_duration: float = 1.0
    max_duration: float = 7.0
    
    # Configurações especiais
    shadow_enabled: bool = True
    shadow_offset: Tuple[int, int] = (2, 2)
    shadow_blur: int = 3
    
class SubtitleStyleManager:
    """Gerenciador de estilos de legendas."""
    
    # Estilos predefinidos baseados em melhores práticas
    STYLES = {
        "netflix": SubtitleStyle(
            font_family="Arial",
            font_size=24,
            font_weight="bold",
            text_color="white",
            background_color="black",
            background_opacity=0.75,
            outline_width=2,
            max_chars_per_line=42,
            chars_per_second=20
        ),
        
        "youtube": SubtitleStyle(
            font_family="Roboto",
            font_size=20,
            font_weight="normal",
            text_color="white",
            background_color="black",
            background_opacity=0.8,
            outline_width=1,
            max_chars_per_line=42,
            chars_per_second=21
        ),
        
        "cinema": SubtitleStyle(
            font_family="Arial",
            font_size=26,
            font_weight="bold",
            text_color="white",
            background_color="transparent",
            background_opacity=0.0,
            outline_color="black",
            outline_width=3,
            max_chars_per_line=45,
            chars_per_second=18,
            shadow_enabled=True
        ),
        
        "modern": SubtitleStyle(
            font_family="Helvetica",
            font_size=22,
            font_weight="medium",
            text_color="#FFFFFF",
            background_color="#000000",
            background_opacity=0.85,
            outline_width=1,
            max_chars_per_line=40,
            chars_per_second=21,
            shadow_enabled=True,
            shadow_offset=(1, 1),
            shadow_blur=2
        ),
        
        "accessibility": SubtitleStyle(
            font_family="Arial",
            font_size=24,
            font_weight="bold",
            text_color="yellow",
            background_color="black",
            background_opacity=0.9,
            outline_color="black",
            outline_width=2,
            max_chars_per_line=37,
            chars_per_second=17,
            shadow_enabled=True
        ),

        "pop": SubtitleStyle(
            font_family="Helvetica",
            font_size=26,
            font_weight="bold",
            text_color="yellow",
            background_color="black",
            background_opacity=0.8,
            outline_color="black",
            outline_width=2,
            max_chars_per_line=38,
            chars_per_second=20,
            shadow_enabled=True,
            shadow_offset=(2, 2),
            shadow_blur=4
        ),
        
        "casquinha": SubtitleStyle(
            font_family="Arial",
            font_size=28,
            font_weight="bold",
            text_color="#FFFF00",  # Amarelo vibrante
            background_color="#000000",  # Preto sólido
            background_opacity=0.85,
            outline_color="#000000",
            outline_width=3,
            max_chars_per_line=35,  # Linhas mais curtas para melhor legibilidade
            chars_per_second=18,  # Velocidade mais lenta para melhor compreensão
            shadow_enabled=True,
            shadow_offset=(2, 2),
            shadow_blur=3,
            position_v="bottom",
            margin_bottom=60  # Margem maior na parte inferior
        ),
        
        "tiktok": SubtitleStyle(
            font_family="Arial",
            font_size=24,  # Será aumentado automaticamente para TikTok
            font_weight="bold",
            text_color="white",
            background_color="black",
            background_opacity=0.7,
            outline_color="black",
            outline_width=2,  # Será aumentado automaticamente para TikTok
            max_chars_per_line=30,  # Linhas mais curtas para tela vertical
            max_lines=2,
            chars_per_second=20,
            shadow_enabled=True,
            shadow_offset=(2, 2),
            shadow_blur=3,
            position_v="bottom",
            margin_bottom=80  # Margem maior para não interferir com UI do TikTok
        ),
        
        "highlighted": SubtitleStyle(
            font_family="Arial Black",
            font_size=52,
            font_weight="bold",
            text_color="white",
            outline_color="black",
            outline_width=2,
            background_color="transparent",
            background_opacity=0.0,
            position_v="bottom",
            margin_bottom=120,
            shadow_enabled=True,
            shadow_offset=(3, 3),
            shadow_blur=3,
            max_chars_per_line=25,
            line_spacing=1.3
        )
    }
    
    @classmethod
    def get_style(cls, style_name: str) -> SubtitleStyle:
        """Obtém um estilo predefinido.
        
        Args:
            style_name: Nome do estilo ('netflix', 'youtube', 'cinema', 'modern', 'accessibility')
            
        Returns:
            Configuração de estilo
        """
        return cls.STYLES.get(style_name.lower(), cls.STYLES["modern"])
    
    @classmethod
    def create_custom_style(cls, **kwargs) -> SubtitleStyle:
        """Cria um estilo personalizado.
        
        Args:
            **kwargs: Parâmetros de estilo a serem sobrescritos
            
        Returns:
            Configuração de estilo personalizada
        """
        base_style = cls.STYLES["modern"]
        custom_params = {}
        
        # Copiar atributos do estilo base
        for field in base_style.__dataclass_fields__:
            custom_params[field] = getattr(base_style, field)
        
        # Aplicar customizações
        custom_params.update(kwargs)
        
        return SubtitleStyle(**custom_params)
    
    @staticmethod
    def generate_ffmpeg_subtitle_filter(style: SubtitleStyle, subtitle_file: str, video_format: str = "standard") -> str:
        """Gera filtro FFmpeg para aplicar estilo às legendas.
        
        Args:
            style: Configuração de estilo
            subtitle_file: Caminho para o arquivo de legendas
            video_format: Formato do vídeo ('tiktok', 'youtube', 'standard')
            
        Returns:
            String do filtro FFmpeg
        """
        # Escapar caracteres especiais no caminho do arquivo
        subtitle_file_escaped = subtitle_file.replace(chr(92), '/').replace(':', '\\:')
        
        # Construir configurações de estilo para FFmpeg
        style_options = []
        
        # Ajustar tamanho da fonte baseado no formato do vídeo
        font_size = style.font_size
        if video_format == "tiktok":
            # Para TikTok (9:16), usar fonte maior para melhor legibilidade em mobile
            font_size = int(style.font_size * 1.3)
        
        style_options.append(f"Fontsize={font_size}")
        
        # Cor do texto (converter de hex para BGR)
        if style.text_color.startswith('#'):
            hex_color = style.text_color[1:]
            # Converter para formato BGR do FFmpeg
            if len(hex_color) == 6:
                r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
                bgr_color = f"{b}{g}{r}"
                style_options.append(f"PrimaryColour=&H{bgr_color}")
        elif style.text_color == "yellow":
            style_options.append("PrimaryColour=&H00FFFF")  # Amarelo em BGR
        elif style.text_color == "white":
            style_options.append("PrimaryColour=&HFFFFFF")  # Branco em BGR
        
        # Contorno (mais espesso para TikTok)
        outline_width = style.outline_width
        if video_format == "tiktok":
            outline_width = max(3, style.outline_width + 1)  # Contorno mais espesso para mobile
        
        if outline_width > 0:
            style_options.append(f"Outline={outline_width}")
            # Cor do contorno
            if style.outline_color.startswith('#'):
                hex_color = style.outline_color[1:]
                if len(hex_color) == 6:
                    r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
                    bgr_color = f"{b}{g}{r}"
                    style_options.append(f"OutlineColour=&H{bgr_color}")
            elif style.outline_color == "black":
                style_options.append("OutlineColour=&H000000")
        
        # Negrito
        if style.font_weight == "bold":
            style_options.append("Bold=1")
        
        # Posicionamento otimizado para diferentes formatos
        if video_format == "tiktok":
            # Para TikTok, posicionar legendas a 30% de baixo para cima
            # Altura TikTok: 1280px, 30% = 384px, mas usar margem de baixo
            style_options.append("MarginV=384")  # 30% de baixo para cima
            style_options.append("Alignment=2")  # Parte inferior centralizada
            # Forçar posição usando PlayResY
            style_options.append("PlayResY=1280")
        else:
            # Posicionamento padrão para outros formatos
            style_options.append(f"MarginV={style.margin_bottom}")
            style_options.append("Alignment=2")  # Centralizado na parte inferior
        
        # Cor de fundo com transparência
        if hasattr(style, 'background_color') and style.background_color and style.background_color != "transparent":
            if style.background_color.startswith('#'):
                hex_color = style.background_color[1:]
                if len(hex_color) == 6:
                    r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
                    bgr_color = f"{b}{g}{r}"
                    # Adicionar transparência baseada na opacidade
                    alpha = int((1.0 - style.background_opacity) * 255)
                    style_options.append(f"BackColour=&H{alpha:02X}{bgr_color}")
            elif style.background_color == "black":
                alpha = int((1.0 - style.background_opacity) * 255)
                style_options.append(f"BackColour=&H{alpha:02X}000000")
        
        # Sombra para melhor legibilidade
        if style.shadow_enabled:
            style_options.append("Shadow=2")  # Sombra ativada
            style_options.append("ShadowColour=&H80000000")  # Sombra preta semi-transparente
        
        # Construir filtro final
        if style_options:
            force_style = ','.join(style_options)
            subtitle_filter = f"subtitles={subtitle_file_escaped}:force_style='{force_style}'"
        else:
            subtitle_filter = f"subtitles={subtitle_file_escaped}"
        
        return subtitle_filter
    
    @staticmethod
    def apply_style_to_srt(srt_content: str, style: SubtitleStyle) -> str:
        """Aplica formatação de estilo ao conteúdo SRT.
        
        Args:
            srt_content: Conteúdo SRT original
            style: Configuração de estilo
            
        Returns:
            Conteúdo SRT com formatação aplicada
        """
        lines = srt_content.strip().split('\n')
        styled_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Linha de número da legenda
            if line.isdigit():
                styled_lines.append(line)
                i += 1
                continue
            
            # Linha de timestamp
            if '-->' in line:
                styled_lines.append(line)
                i += 1
                continue
            
            # Linha de texto da legenda
            if line and not line.isdigit() and '-->' not in line:
                # Aplicar quebras de linha baseadas no estilo
                formatted_text = SubtitleStyleManager._format_text_for_style(line, style)
                styled_lines.append(formatted_text)
                i += 1
                continue
            
            # Linha vazia
            if not line:
                styled_lines.append('')
                i += 1
                continue
            
            i += 1
        
        return '\n'.join(styled_lines)
    
    @staticmethod
    def _format_text_for_style(text: str, style: SubtitleStyle) -> str:
        """Formata texto de acordo com o estilo.
        
        Args:
            text: Texto original
            style: Configuração de estilo
            
        Returns:
            Texto formatado
        """
        # Quebrar texto em linhas respeitando o limite de caracteres
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # Verificar se adicionar a palavra excede o limite
            test_line = f"{current_line} {word}".strip()
            
            if len(test_line) <= style.max_chars_per_line:
                current_line = test_line
            else:
                # Adicionar linha atual e começar nova
                if current_line:
                    lines.append(current_line)
                current_line = word
                
                # Verificar limite de linhas
                if len(lines) >= style.max_lines:
                    break
        
        # Adicionar última linha
        if current_line and len(lines) < style.max_lines:
            lines.append(current_line)
        
        return '\n'.join(lines)
    
    @staticmethod
    def validate_timing(start_time: float, end_time: float, text: str, style: SubtitleStyle) -> Tuple[float, float]:
        """Valida e ajusta timing de legendas baseado no estilo.
        
        Args:
            start_time: Tempo de início em segundos
            end_time: Tempo de fim em segundos
            text: Texto da legenda
            style: Configuração de estilo
            
        Returns:
            Tupla com tempos ajustados (start, end)
        """
        # Calcular duração baseada no número de caracteres
        char_count = len(text.replace('\n', ''))
        recommended_duration = char_count / style.chars_per_second
        
        # Aplicar limites mínimo e máximo
        recommended_duration = max(style.min_duration, recommended_duration)
        recommended_duration = min(style.max_duration, recommended_duration)
        
        # Ajustar tempo de fim se necessário
        current_duration = end_time - start_time
        
        if current_duration < recommended_duration:
            end_time = start_time + recommended_duration
        elif current_duration > style.max_duration:
            end_time = start_time + style.max_duration
        
        return start_time, end_time

def get_available_styles() -> Dict[str, str]:
    """Retorna lista de estilos disponíveis com descrições.
    
    Returns:
        Dicionário com nomes e descrições dos estilos
    """
    return {
        "netflix": "Estilo Netflix - Fonte bold, alta legibilidade",
        "youtube": "Estilo YouTube - Moderno e limpo",
        "cinema": "Estilo Cinema - Elegante com sombra",
        "modern": "Estilo Moderno - Equilibrado e profissional",
        "accessibility": "Estilo Acessibilidade - Alto contraste para deficientes visuais",
        "casquinha": "Estilo Casquinha - Texto amarelo vibrante com fundo preto, ideal para conteúdo divertido",
        "tiktok": "Estilo TikTok - Otimizado para formato vertical 9:16 e dispositivos móveis",
        "highlighted": "Estilo Highlighted - Para destaque de palavras-chave com fonte grande e contorno forte"
    }

if __name__ == "__main__":
    # Exemplo de uso
    style_manager = SubtitleStyleManager()
    
    # Testar estilo Netflix
    netflix_style = style_manager.get_style("netflix")
    print(f"Estilo Netflix: {netflix_style}")
    
    # Criar estilo personalizado
    custom_style = style_manager.create_custom_style(
        font_size=28,
        text_color="#FFD700",  # Dourado
        background_opacity=0.9
    )
    print(f"Estilo personalizado: {custom_style}")
    
    # Mostrar estilos disponíveis
    print("\nEstilos disponíveis:")
    for name, description in get_available_styles().items():
        print(f"  {name}: {description}")