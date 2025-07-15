"""Generates subtitles from an audio file using Google Gemini 2.0 Flash."""
import os
import sys
from pathlib import Path

# Adicionar o diretório src ao path para imports
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.append(str(src_dir))

from gemini_subtitle_client import GeminiSubtitleClient, generate_subtitles_quick
import numpy as np
from scipy.io.wavfile import write # For placeholder fallback

def srt_time_format(seconds):
    """Converts seconds to SRT time format (HH:MM:SS,ms)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def generate_subtitles(audio_files, output_dir):
    """
    Generates subtitles from audio files using Google Gemini 2.0 Flash.

    Args:
        audio_files: List of audio file paths or single audio file path.
        output_dir: The directory where the subtitle file will be saved.

    Returns:
        The path to the generated .srt subtitles file.
    """
    print(f"  -> Generating subtitles using Gemini 2.0 Flash...")
    
    # Garantir que audio_files seja uma lista
    if isinstance(audio_files, str):
        audio_files = [audio_files]
    
    subtitle_path = os.path.join(output_dir, "subtitles.srt")
    
    try:
        # Inicializar cliente Gemini
        client = GeminiSubtitleClient()
        
        # Gerar legendas para todos os arquivos de áudio
        all_subtitles = []
        subtitle_counter = 1
        
        for i, audio_file in enumerate(audio_files):
            if not os.path.exists(audio_file):
                print(f"     - Aviso: Arquivo não encontrado: {audio_file}")
                continue
                
            print(f"     - Processando arquivo {i+1}/{len(audio_files)}: {os.path.basename(audio_file)}")
            
            # Gerar legendas para este arquivo
            subtitle_content = client.generate_subtitles(audio_file, language="pt-BR")
            
            # Processar e ajustar numeração das legendas
            if subtitle_content.strip():
                lines = subtitle_content.strip().split('\n')
                processed_lines = []
                
                for line in lines:
                    line = line.strip()
                    if line.isdigit():  # Linha de número da legenda
                        processed_lines.append(str(subtitle_counter))
                        subtitle_counter += 1
                    else:
                        processed_lines.append(line)
                
                all_subtitles.extend(processed_lines)
                all_subtitles.append("")  # Linha vazia entre arquivos
        
        # Salvar todas as legendas em um arquivo
        with open(subtitle_path, "w", encoding="utf-8") as f:
            f.write("\n".join(all_subtitles))
        
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

if __name__ == '__main__':
    # Example usage for testing
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not set.")
    else:
        # Testar com arquivo de áudio existente
        test_audio_file = "output/video_um_robô_explorando_uma_cidade_futurística_20250715_201003/audio/audio_scene_01.mp3"
        test_output_dir = "test_output_subtitles"
        os.makedirs(test_output_dir, exist_ok=True)
        
        if os.path.exists(test_audio_file):
            path = generate_subtitles(test_audio_file, test_output_dir)
            print(f"\nGenerated subtitle file at: {path}")
        else:
            print(f"Test audio file not found: {test_audio_file}")
            print("Please provide a valid audio file path for testing.")