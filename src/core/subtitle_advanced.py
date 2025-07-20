"""Gerador avançado de legendas ASS (Advanced SubStation Alpha).

Este módulo implementa a geração de legendas ASS com suporte a formatação
avançada, incluindo cores inline, fundos coloridos e estilos personalizados
para o estilo "highlighted subtitle".
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Adicionar o diretório raiz ao path para imports
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from utils.keyword_highlighter import KeywordHighlighter
from core.subtitle_styles import SubtitleStyle

@dataclass
class ASSEvent:
    """Representa um evento de legenda ASS."""
    start_time: str
    end_time: str
    text: str
    style: str = "Default"
    
def seconds_to_ass_time(seconds: float) -> str:
    """Converte segundos para formato de tempo ASS (H:MM:SS.CC).
    
    Args:
        seconds: Tempo em segundos
        
    Returns:
        Tempo no formato ASS
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centiseconds = int((seconds - int(seconds)) * 100)
    
    return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"

def ass_time_to_seconds(time_str: str) -> float:
    """Converte tempo ASS para segundos.
    
    Args:
        time_str: Tempo no formato ASS (H:MM:SS.CC)
        
    Returns:
        Tempo em segundos
    """
    try:
        # Formato: H:MM:SS.CC
        time_part, centiseconds_part = time_str.split('.')
        time_components = time_part.split(':')
        
        hours = int(time_components[0])
        minutes = int(time_components[1])
        seconds = int(time_components[2])
        centiseconds = int(centiseconds_part)
        
        total_seconds = hours * 3600 + minutes * 60 + seconds + centiseconds / 100.0
        return total_seconds
    except Exception as e:
        print(f"Erro ao converter timestamp ASS '{time_str}': {e}")
        return 0.0

class ASSGenerator:
    """Gerador de legendas ASS com formatação avançada."""
    
    def __init__(self, video_width: int = 1280, video_height: int = 720):
        """Inicializa o gerador ASS.
        
        Args:
            video_width: Largura do vídeo
            video_height: Altura do vídeo
        """
        self.video_width = video_width
        self.video_height = video_height
        self.highlighter = KeywordHighlighter()
        self.events = []
        
    def _generate_header(self, style: SubtitleStyle) -> str:
        """Gera cabeçalho do arquivo ASS.
        
        Args:
            style: Configurações de estilo
            
        Returns:
            Cabeçalho ASS
        """
        header = f"""[Script Info]
Title: AI Video GPT Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: {self.video_width}
PlayResY: {self.video_height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""
        
        # Converter cor do texto para formato ASS
        primary_color = self._convert_color_to_ass(style.text_color)
        outline_color = self._convert_color_to_ass(style.outline_color)
        
        # Configurar cor de fundo
        if hasattr(style, 'background_color') and style.background_color != "transparent":
            back_color = self._convert_color_to_ass(style.background_color, style.background_opacity)
        else:
            back_color = "&H80000000"  # Transparente
        
        # Configurar alinhamento
        alignment = 2  # Centralizado na parte inferior
        
        # Configurar margem vertical baseada no formato
        margin_v = style.margin_bottom
        if self.video_height == 1280:  # TikTok format
            margin_v = 384  # 30% de baixo para cima
        
        # Estilo padrão
        default_style = f"Style: Default,{style.font_family},{style.font_size},{primary_color},&Hffffff,{outline_color},{back_color},{1 if style.font_weight == 'bold' else 0},0,0,0,100,100,0,0,1,{style.outline_width},{2 if style.shadow_enabled else 0},{alignment},10,10,{margin_v},1\n"
        
        # Estilo para palavras destacadas
        highlighted_style = f"Style: Highlighted,{style.font_family},{style.font_size},&Hffffff,&Hffffff,&H000000,&H80000000,1,0,0,0,100,100,0,0,1,{style.outline_width + 1},2,{alignment},10,10,{margin_v},1\n"
        
        header += default_style + highlighted_style
        header += "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        
        return header
    
    def _convert_color_to_ass(self, color: str, opacity: float = 1.0) -> str:
        """Converte cor para formato ASS.
        
        Args:
            color: Cor em formato hex ou nome
            opacity: Opacidade (0.0 a 1.0)
            
        Returns:
            Cor no formato ASS (&HAABBGGRR)
        """
        # Mapa de cores nomeadas
        color_map = {
            'white': '#FFFFFF',
            'black': '#000000',
            'red': '#FF0000',
            'green': '#00FF00',
            'blue': '#0000FF',
            'yellow': '#FFFF00',
            'cyan': '#00FFFF',
            'magenta': '#FF00FF'
        }
        
        # Converter nome para hex se necessário
        if color in color_map:
            color = color_map[color]
        
        # Processar cor hex
        if color.startswith('#') and len(color) == 7:
            # Remover #
            hex_color = color[1:]
            
            # Extrair componentes RGB
            r = hex_color[0:2]
            g = hex_color[2:4]
            b = hex_color[4:6]
            
            # Calcular alpha baseado na opacidade
            alpha = int((1.0 - opacity) * 255)
            
            # Retornar em formato ASS (AABBGGRR)
            return f"&H{alpha:02X}{b}{g}{r}"
        
        # Cor padrão (branco)
        return "&Hffffff"
    
    def parse_srt_to_events(self, srt_content: str, highlight_keywords: bool = True, 
                           auto_detect: bool = True) -> List[ASSEvent]:
        """Converte conteúdo SRT para eventos ASS.
        
        Args:
            srt_content: Conteúdo do arquivo SRT
            highlight_keywords: Se deve aplicar destaque de palavras-chave
            auto_detect: Se deve detectar palavras-chave automaticamente
            
        Returns:
            Lista de eventos ASS
        """
        events = []
        lines = srt_content.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Linha de número da legenda
            if line.isdigit():
                # Próxima linha deve ser timestamp
                if i + 1 < len(lines) and '-->' in lines[i + 1]:
                    timestamp_line = lines[i + 1].strip()
                    start_time, end_time = timestamp_line.split(' --> ')
                    
                    # Converter timestamps SRT para ASS
                    start_ass = self._srt_to_ass_time(start_time)
                    end_ass = self._srt_to_ass_time(end_time)
                    
                    # Próxima linha deve ser o texto
                    if i + 2 < len(lines) and lines[i + 2].strip():
                        text_line = lines[i + 2].strip()
                        
                        # Aplicar destaque de palavras-chave se solicitado
                        if highlight_keywords:
                            processed_text = self.highlighter.generate_ass_tags(
                                text_line, auto_detect=auto_detect
                            )
                        else:
                            processed_text = text_line
                        
                        # Criar evento ASS
                        event = ASSEvent(
                            start_time=start_ass,
                            end_time=end_ass,
                            text=processed_text,
                            style="Default"
                        )
                        events.append(event)
                
                i += 3  # Pular número, timestamp e texto
                continue
            
            i += 1
        
        return events
    
    def _srt_to_ass_time(self, srt_time: str) -> str:
        """Converte timestamp SRT para formato ASS.
        
        Args:
            srt_time: Timestamp SRT (HH:MM:SS,mmm)
            
        Returns:
            Timestamp ASS (H:MM:SS.CC)
        """
        try:
            # Formato SRT: HH:MM:SS,mmm
            time_part, millis_part = srt_time.split(',')
            hours, minutes, seconds = map(int, time_part.split(':'))
            millis = int(millis_part)
            
            # Converter para centésimos
            centiseconds = millis // 10
            
            return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
        except Exception as e:
            print(f"Erro ao converter timestamp SRT '{srt_time}': {e}")
            return "0:00:00.00"
    
    def generate_ass_content(self, srt_content: str, style: SubtitleStyle, 
                           highlight_keywords: bool = True, auto_detect: bool = True) -> str:
        """Gera conteúdo completo do arquivo ASS.
        
        Args:
            srt_content: Conteúdo SRT original
            style: Configurações de estilo
            highlight_keywords: Se deve aplicar destaque
            auto_detect: Se deve detectar palavras-chave automaticamente
            
        Returns:
            Conteúdo completo do arquivo ASS
        """
        # Gerar cabeçalho
        content = self._generate_header(style)
        
        # Converter SRT para eventos ASS
        events = self.parse_srt_to_events(srt_content, highlight_keywords, auto_detect)
        
        # Adicionar eventos
        for event in events:
            line = f"Dialogue: 0,{event.start_time},{event.end_time},{event.style},,0,0,0,,{event.text}\n"
            content += line
        
        return content
    
    def save_ass_file(self, srt_content: str, output_path: str, style: SubtitleStyle,
                     highlight_keywords: bool = True, auto_detect: bool = True) -> str:
        """Salva arquivo ASS com formatação avançada.
        
        Args:
            srt_content: Conteúdo SRT original
            output_path: Caminho para salvar o arquivo ASS
            style: Configurações de estilo
            highlight_keywords: Se deve aplicar destaque
            auto_detect: Se deve detectar palavras-chave automaticamente
            
        Returns:
            Caminho do arquivo ASS gerado
        """
        # Gerar conteúdo ASS
        ass_content = self.generate_ass_content(
            srt_content, style, highlight_keywords, auto_detect
        )
        
        # Salvar arquivo
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)
        
        return output_path
    
    def add_custom_highlight(self, word: str, color: str, text_color: str = "white"):
        """Adiciona destaque personalizado.
        
        Args:
            word: Palavra a ser destacada
            color: Cor de fundo
            text_color: Cor do texto
        """
        self.highlighter.add_custom_highlight(word, color, text_color)
    
    def get_ffmpeg_filter(self, ass_file_path: str) -> str:
        """Gera filtro FFmpeg para aplicar legendas ASS.
        
        Args:
            ass_file_path: Caminho para o arquivo ASS
            
        Returns:
            String do filtro FFmpeg
        """
        # Escapar caracteres especiais no caminho
        escaped_path = ass_file_path.replace(chr(92), '/').replace(':', '\\:')
        
        return f"ass={escaped_path}"

def convert_srt_to_highlighted_ass(srt_file: str, output_dir: str, style: SubtitleStyle,
                                  video_width: int = 1280, video_height: int = 720,
                                  highlight_keywords: bool = True, auto_detect: bool = True) -> str:
    """Converte arquivo SRT para ASS com destaque de palavras-chave.
    
    Args:
        srt_file: Caminho do arquivo SRT
        output_dir: Diretório de saída
        style: Configurações de estilo
        video_width: Largura do vídeo
        video_height: Altura do vídeo
        highlight_keywords: Se deve aplicar destaque
        auto_detect: Se deve detectar palavras-chave automaticamente
        
    Returns:
        Caminho do arquivo ASS gerado
    """
    # Ler arquivo SRT
    with open(srt_file, 'r', encoding='utf-8') as f:
        srt_content = f.read()
    
    # Criar gerador ASS
    generator = ASSGenerator(video_width, video_height)
    
    # Gerar nome do arquivo ASS
    srt_name = os.path.splitext(os.path.basename(srt_file))[0]
    ass_file = os.path.join(output_dir, f"{srt_name}_highlighted.ass")
    
    # Gerar e salvar arquivo ASS
    return generator.save_ass_file(
        srt_content, ass_file, style, highlight_keywords, auto_detect
    )

if __name__ == "__main__":
    # Exemplo de uso
    from core.subtitle_styles import SubtitleStyleManager
    
    # Criar estilo de teste
    style = SubtitleStyleManager.get_style("tiktok")
    
    # Criar gerador ASS
    generator = ASSGenerator(720, 1280)  # TikTok format
    
    # Adicionar destaque personalizado
    generator.add_custom_highlight("TESTE", "#FF0000")  # Vermelho
    
    # Conteúdo SRT de exemplo
    srt_example = """1
00:00:00,000 --> 00:00:03,000
Let's CREATE something AMAZING!

2
00:00:03,500 --> 00:00:06,500
This is a {SPECIAL:blue} moment to celebrate!

3
00:00:07,000 --> 00:00:10,000
BUILD your dreams and make them REAL!
"""
    
    # Gerar ASS
    ass_content = generator.generate_ass_content(srt_example, style)
    
    print("Conteúdo ASS gerado:")
    print(ass_content)
    
    # Salvar arquivo de teste
    test_output = "test_highlighted.ass"
    generator.save_ass_file(srt_example, test_output, style)
    print(f"\nArquivo ASS salvo: {test_output}")
    
    # Mostrar filtro FFmpeg
    print(f"Filtro FFmpeg: {generator.get_ffmpeg_filter(test_output)}")