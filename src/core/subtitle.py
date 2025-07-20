"""Generates subtitles from an audio file using Google Gemini 2.0 Flash."""
import os
import sys
import json
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from config.gemini_subtitle_client import GeminiSubtitleClient, generate_subtitles_quick
import numpy as np
from scipy.io.wavfile import write # For placeholder fallback
from core.subtitle_styles import SubtitleStyleManager, SubtitleStyle
from core.subtitle_advanced import ASSGenerator, convert_srt_to_highlighted_ass
from utils.keyword_highlighter import KeywordHighlighter
from core.subtitle_script_sync import ScriptSubtitleSynchronizer

def generate_subtitles_from_script_sync(script_path: str, audio_files: list, output_dir: str, style_name: str = "modern") -> str:
    """
    Função de conveniência para gerar legendas a partir do roteiro usando sincronização.
    
    Args:
        script_path: Caminho para o arquivo script.json
        audio_files: Lista de arquivos de áudio
        output_dir: Diretório de saída
        style_name: Nome do estilo de legenda
        
    Returns:
        Caminho do arquivo SRT gerado
    """
    import os
    
    # Criar diretório de saída se não existir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Usar o sincronizador para gerar as legendas
    synchronizer = ScriptSubtitleSynchronizer()
    return synchronizer.generate_subtitles_from_script(
        script_path, audio_files, output_dir, style_name
    )

def detect_script_language(script_data):
    """Detecta o idioma do roteiro baseado no conteúdo das narrações.
    
    Args:
        script_data: Caminho para o arquivo de roteiro JSON ou dicionário com dados do roteiro
        
    Returns:
        str: Código do idioma ('pt-BR' ou 'en')
    """
    try:
        # Se for string, é um caminho de arquivo
        if isinstance(script_data, str):
            if not os.path.exists(script_data):
                print(f"     - Script não encontrado: {script_data}, usando inglês como padrão")
                return "en"
            with open(script_data, 'r', encoding='utf-8') as f:
                script_content = json.load(f)
        # Se for dicionário, usar diretamente
        elif isinstance(script_data, dict):
            script_content = script_data
        else:
            print(f"     - Erro na detecção de idioma: tipo de dados inválido, usando inglês como padrão")
            return "en"
        
        # Extrair todas as narrações
        narrations = []
        if 'scenes' in script_content:
            for scene in script_content['scenes']:
                if 'narration' in scene:
                    narrations.append(scene['narration'])
        
        # Analisar o texto para detectar idioma
        all_text = ' '.join(narrations).lower()
        
        # Palavras comuns em português
        pt_words = ['o', 'a', 'de', 'do', 'da', 'em', 'um', 'uma', 'para', 'com', 'não', 'que', 'se', 'por', 'mais', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'suas', 'numa', 'pelos', 'pelas', 'esse', 'eles', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'têm', 'numa', 'pelos', 'pelas', 'essas', 'esses', 'pelas', 'pelos', 'dela', 'deles', 'desta', 'deste', 'disto', 'daquela', 'daquele', 'daquilo', 'lhe', 'lhes', 'me', 'mim', 'comigo', 'te', 'ti', 'contigo', 'si', 'consigo', 'conosco', 'convosco']
        
        # Palavras comuns em inglês
        en_words = ['the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 'for', 'on', 'are', 'as', 'with', 'his', 'they', 'i', 'at', 'be', 'this', 'have', 'from', 'or', 'one', 'had', 'by', 'word', 'but', 'not', 'what', 'all', 'were', 'we', 'when', 'your', 'can', 'said', 'there', 'each', 'which', 'she', 'do', 'how', 'their', 'if', 'will', 'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'into', 'him', 'has', 'two', 'more', 'very', 'after', 'words', 'first', 'where', 'much', 'through', 'back', 'years', 'work', 'came', 'right', 'used', 'take', 'three', 'states', 'himself', 'few', 'house', 'use', 'during', 'without', 'again', 'place', 'american', 'around', 'however', 'home', 'small', 'found', 'mrs', 'thought', 'went', 'say', 'part', 'once', 'general', 'high', 'upon', 'school', 'every', 'don', 'does', 'got', 'united', 'left', 'number', 'course', 'war', 'until', 'always', 'away', 'something', 'fact', 'though', 'water', 'less', 'public', 'put', 'think', 'almost', 'hand', 'enough', 'far', 'took', 'head', 'yet', 'government', 'system', 'better', 'set', 'told', 'nothing', 'night', 'end', 'why', 'called', 'didn', 'eyes', 'find', 'going', 'look', 'asked', 'later', 'knew', 'let', 'great', 'year', 'come', 'since', 'against', 'go', 'came', 'right', 'used', 'take', 'three']
        
        # Contar palavras em cada idioma
        pt_count = sum(1 for word in pt_words if word in all_text)
        en_count = sum(1 for word in en_words if word in all_text)
        
        print(f"     - Detecção de idioma: PT={pt_count}, EN={en_count}")
        
        # Determinar idioma baseado na contagem
        if pt_count > en_count:
            return "pt-BR"
        else:
            return "en"
            
    except Exception as e:
        print(f"     - Erro na detecção de idioma: {e}, usando inglês como padrão")
        return "en"

def srt_time_format(seconds):
    """Converts seconds to SRT time format (HH:MM:SS,ms)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def _srt_time_to_seconds(time_str):
    """Converts SRT time format (HH:MM:SS,ms) to seconds."""
    try:
        # Formato: HH:MM:SS,ms
        time_part, millis_part = time_str.split(',')
        hours, minutes, seconds = map(int, time_part.split(':'))
        millis = int(millis_part)
        
        total_seconds = hours * 3600 + minutes * 60 + seconds + millis / 1000.0
        return total_seconds
    except Exception as e:
        print(f"Erro ao converter timestamp '{time_str}': {e}")
        return 0.0

def break_subtitles_into_words(srt_content):
    """Quebra legendas SRT em palavras individuais mantendo sincronização.
    
    Args:
        srt_content: Conteúdo SRT original
        
    Returns:
        Conteúdo SRT com uma palavra por legenda
    """
    lines = srt_content.strip().split('\n')
    word_subtitles = []
    subtitle_counter = 1
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Linha de número da legenda
        if line.isdigit():
            # Próxima linha deve ser timestamp
            if i + 1 < len(lines) and '-->' in lines[i + 1]:
                timestamp_line = lines[i + 1].strip()
                start_time, end_time = timestamp_line.split(' --> ')
                
                # Próxima linha deve ser o texto
                if i + 2 < len(lines) and lines[i + 2].strip():
                    text_line = lines[i + 2].strip()
                    
                    # Quebrar texto em palavras
                    words = text_line.split()
                    
                    if words:
                        # Calcular duração total da legenda
                        start_seconds = _srt_time_to_seconds(start_time)
                        end_seconds = _srt_time_to_seconds(end_time)
                        total_duration = end_seconds - start_seconds
                        
                        # Distribuir tempo entre palavras
                        word_duration = total_duration / len(words)
                        
                        for j, word in enumerate(words):
                            # Calcular tempo para esta palavra
                            word_start = start_seconds + (j * word_duration)
                            word_end = start_seconds + ((j + 1) * word_duration)
                            
                            # Adicionar legenda para esta palavra
                            word_subtitles.append(str(subtitle_counter))
                            word_subtitles.append(f"{srt_time_format(word_start)} --> {srt_time_format(word_end)}")
                            word_subtitles.append(word)
                            word_subtitles.append("")  # Linha vazia
                            
                            subtitle_counter += 1
                
                i += 3  # Pular número, timestamp e texto
                continue
        
        i += 1
    
    return "\n".join(word_subtitles)

def generate_highlighted_subtitles(audio_files: list, output_dir: str, 
                                 style_name: str = "highlighted",
                                 video_width: int = 1280, video_height: int = 720,
                                 highlight_keywords: bool = True, auto_detect: bool = True,
                                 custom_highlights: dict = None,
                                 break_into_words: bool = False,
                                 language: str = "auto") -> dict:
    """Gera legendas com destaque de palavras-chave.
    
    Args:
        audio_files: Lista de arquivos de áudio
        output_dir: Diretório de saída
        style_name: Nome do estilo de legenda
        video_width: Largura do vídeo
        video_height: Altura do vídeo
        highlight_keywords: Se deve aplicar destaque
        auto_detect: Se deve detectar palavras-chave automaticamente
        custom_highlights: Destaques personalizados {palavra: cor}
        break_into_words: Se deve quebrar em palavras individuais
        language: Idioma das legendas
        
    Returns:
        Dicionário com caminhos dos arquivos gerados
    """
    print(f"\n🎯 Gerando legendas com destaque de palavras-chave...")
    print(f"📁 Diretório de saída: {output_dir}")
    print(f"🎨 Estilo: {style_name}")
    print(f"📐 Resolução: {video_width}x{video_height}")
    
    # Criar diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Obter estilo
    style = SubtitleStyleManager.get_style(style_name)
    if not style:
        print(f"⚠️ Estilo '{style_name}' não encontrado, usando 'highlighted'")
        style = SubtitleStyleManager.get_style("highlighted")
    
    # Criar gerador ASS
    ass_generator = ASSGenerator(video_width, video_height)
    
    # Adicionar destaques personalizados
    if custom_highlights:
        for word, color in custom_highlights.items():
            ass_generator.add_custom_highlight(word, color)
    
    results = {
        'srt_files': [],
        'ass_files': [],
        'style_used': style_name,
        'highlights_applied': highlight_keywords
    }
    
    # Processar cada arquivo de áudio
    for i, audio_file in enumerate(audio_files):
        print(f"\n🎵 Processando áudio {i+1}/{len(audio_files)}: {os.path.basename(audio_file)}")
        
        try:
            # Gerar legendas SRT primeiro
            srt_file = generate_subtitles(
                audio_files=[audio_file],
                output_dir=output_dir,
                word_by_word=break_into_words
            )
            
            if srt_file:
                results['srt_files'].append(srt_file)
                
                print(f"✅ Legendas SRT geradas: {os.path.basename(srt_file)}")
                
                # Converter para ASS com destaque
                if highlight_keywords:
                    print(f"🎨 Aplicando destaque de palavras-chave...")
                    
                    ass_file = convert_srt_to_highlighted_ass(
                        srt_file=srt_file,
                        output_dir=output_dir,
                        style=style,
                        video_width=video_width,
                        video_height=video_height,
                        highlight_keywords=highlight_keywords,
                        auto_detect=auto_detect
                    )
                    
                    results['ass_files'].append(ass_file)
                    print(f"✨ Legendas ASS com destaque geradas: {os.path.basename(ass_file)}")
                    
                    # Mostrar filtro FFmpeg
                    ffmpeg_filter = ass_generator.get_ffmpeg_filter(ass_file)
                    print(f"🎬 Filtro FFmpeg: {ffmpeg_filter}")
                else:
                    print(f"ℹ️ Destaque desabilitado, usando apenas SRT")
            
        except Exception as e:
            print(f"❌ Erro ao processar {audio_file}: {e}")
            continue
    
    # Resumo final
    print(f"\n📊 Resumo da geração:")
    print(f"   📄 Arquivos SRT: {len(results['srt_files'])}")
    print(f"   🎨 Arquivos ASS: {len(results['ass_files'])}")
    print(f"   🎯 Destaque aplicado: {'Sim' if highlight_keywords else 'Não'}")
    print(f"   🎪 Estilo usado: {style_name}")
    
    return results

def generate_subtitles_from_script_sync(script_path: str, audio_files: list, output_dir: str, style_name: str = "modern") -> str:
    """
    Gera legendas a partir do roteiro usando o método de sincronização.
    
    Args:
        script_path: Caminho para o arquivo script.json
        audio_files: Lista de arquivos de áudio
        output_dir: Diretório de saída
        style_name: Nome do estilo de legenda
        
    Returns:
        Caminho do arquivo SRT gerado
    """
    import os
    from .subtitle_script_sync import ScriptSubtitleSynchronizer
    
    # Criar diretório de saída
    os.makedirs(output_dir, exist_ok=True)
    
    # Inicializar sincronizador
    synchronizer = ScriptSubtitleSynchronizer()
    
    # Gerar legendas
    return synchronizer.generate_subtitles_from_script(
        script_path, audio_files, output_dir, style_name
    )

def generate_subtitles(audio_files, output_dir, script_path=None, word_by_word=False):
    """
    Generates subtitles from audio files using Google Gemini 2.0 Flash.
    
    NOTA: Para melhor precisão e economia, use generate_subtitles_from_script_sync()
    que não requer transcrição e usa o roteiro existente.

    Args:
        audio_files: List of audio file paths or single audio file path.
        output_dir: The directory where the subtitle file will be saved.
        script_path: Path to the script.json file for language detection (optional).
        word_by_word: Se True, quebra legendas em palavras individuais (padrão: False).

    Returns:
        The path to the generated .srt subtitles file.
    """
    print(f"  -> Generating subtitles using Gemini 2.0 Flash...")
    
    # Garantir que audio_files seja uma lista
    if isinstance(audio_files, str):
        audio_files = [audio_files]
    
    subtitle_path = os.path.join(output_dir, "subtitles.srt")
    
    # Detectar idioma do roteiro
    if script_path:
        detected_language = detect_script_language(script_path)
        print(f"     - Idioma detectado: {detected_language}")
    else:
        detected_language = "en"  # Padrão inglês se não houver script
        print(f"     - Usando idioma padrão: {detected_language}")
    
    try:
        # Inicializar cliente Gemini
        client = GeminiSubtitleClient()
        
        # Gerar legendas para todos os arquivos de áudio
        all_subtitles = []
        subtitle_counter = 1
        time_offset = 0.0  # Offset de tempo acumulado
        
        for i, audio_file in enumerate(audio_files):
            if not os.path.exists(audio_file):
                print(f"     - Aviso: Arquivo não encontrado: {audio_file}")
                continue
                
            print(f"     - Processando arquivo {i+1}/{len(audio_files)}: {os.path.basename(audio_file)}")
            
            # Gerar legendas para este arquivo
            subtitle_content = client.generate_subtitles(audio_file, language=detected_language)
            
            # Processar e ajustar numeração e timing das legendas
            if subtitle_content.strip():
                lines = subtitle_content.strip().split('\n')
                processed_lines = []
                max_end_time = 0.0
                
                i_line = 0
                while i_line < len(lines):
                    line = lines[i_line].strip()
                    
                    if line.isdigit():  # Linha de número da legenda
                        processed_lines.append(str(subtitle_counter))
                        subtitle_counter += 1
                        
                        # Próxima linha deve ser o timestamp
                        if i_line + 1 < len(lines):
                            timestamp_line = lines[i_line + 1].strip()
                            if '-->' in timestamp_line:
                                # Ajustar timestamps com offset
                                start_time, end_time = timestamp_line.split(' --> ')
                                
                                # Converter para segundos, aplicar offset e converter de volta
                                start_seconds = _srt_time_to_seconds(start_time) + time_offset
                                end_seconds = _srt_time_to_seconds(end_time) + time_offset
                                
                                # Atualizar tempo máximo
                                max_end_time = max(max_end_time, end_seconds)
                                
                                # Converter de volta para formato SRT
                                new_timestamp = f"{srt_time_format(start_seconds)} --> {srt_time_format(end_seconds)}"
                                processed_lines.append(new_timestamp)
                                
                                i_line += 2  # Pular número e timestamp
                                continue
                    
                    processed_lines.append(line)
                    i_line += 1
                
                all_subtitles.extend(processed_lines)
                all_subtitles.append("")  # Linha vazia entre arquivos
                
                # Atualizar offset para o próximo arquivo (com pequeno gap)
                time_offset = max_end_time + 0.5  # 0.5 segundos de gap entre arquivos
        
        # Aplicar quebra palavra por palavra se solicitado
        final_content = "\n".join(all_subtitles)
        if word_by_word:
            print(f"     - Aplicando quebra palavra por palavra...")
            final_content = break_subtitles_into_words(final_content)
        
        # Salvar todas as legendas em um arquivo
        with open(subtitle_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        
        print(f"     - Legendas salvas em: {subtitle_path}")
        
        # Estimar custo (assumindo ~30 segundos por arquivo de áudio)
        estimated_minutes = len(audio_files) * 0.5  # 30 segundos = 0.5 minutos
        estimated_cost = client.estimate_cost(estimated_minutes)
        print(f"     - Custo estimado: ${estimated_cost:.4f} USD")
        
        return subtitle_path

    except Exception as e:
        print(f"     - Erro ao gerar legendas com Gemini: {e}")
        # Fallback para arquivo de placeholder
        print("     - Criando arquivo de legenda placeholder...")
        with open(subtitle_path, "w", encoding="utf-8") as f:
            f.write("1\n00:00:00,000 --> 00:00:05,000\nLegenda não pôde ser gerada.\n\n")
            f.write("2\n00:00:05,000 --> 00:00:10,000\nVerifique a configuração do Gemini.\n")
        return subtitle_path

def apply_subtitle_style(srt_content: str, style: SubtitleStyle) -> str:
    """Aplica estilo às legendas SRT.
    
    Args:
        srt_content: Conteúdo SRT original
        style: Configurações de estilo
        
    Returns:
        Conteúdo SRT com estilo aplicado
    """
    # Por enquanto, retorna o conteúdo original
    # Em implementações futuras, pode aplicar formatação específica
    return srt_content

def generate_subtitles_from_script_sync(script_path, audio_files, output_dir, style_name="default"):
    """
    Função de conveniência para gerar legendas a partir de um roteiro,
    sincronizando com arquivos de áudio.
    
    Args:
        script_path: Caminho para o arquivo de roteiro JSON
        audio_files: Lista de caminhos para arquivos de áudio
        output_dir: Diretório para salvar as legendas
        style_name: Nome do estilo de legenda a ser aplicado
        
    Returns:
        str: Caminho para o arquivo de legenda gerado
    """
    import os
    from core.subtitle_script_sync import ScriptSubtitleSynchronizer
    
    # Criar diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Inicializar sincronizador
    synchronizer = ScriptSubtitleSynchronizer()
    
    # Gerar legendas
    subtitle_file = synchronizer.generate_subtitles_from_script(
        script_path=script_path,
        audio_files=audio_files,
        output_dir=output_dir,
        style_name=style_name
    )
    
    return subtitle_file

if __name__ == '__main__':
    # Example usage for testing
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set.")
    else:
        # Testar com arquivo de áudio existente
        test_audio_file = "outputs/videos/video_um_robô_explorando_uma_cidade_futurística_20250715_201003/audio/audio_scene_01.mp3"
        test_output_dir = "test_output_subtitles"
        os.makedirs(test_output_dir, exist_ok=True)
        
        if os.path.exists(test_audio_file):
            path = generate_subtitles(test_audio_file, test_output_dir)
            print(f"\nGenerated subtitle file at: {path}")
        else:
            print(f"Test audio file not found: {test_audio_file}")
            print("Please provide a valid audio file path for testing.")