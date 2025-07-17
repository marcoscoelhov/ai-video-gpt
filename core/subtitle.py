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

def generate_subtitles(audio_files, output_dir, script_path=None):
    """
    Generates subtitles from audio files using Google Gemini 2.0 Flash.

    Args:
        audio_files: List of audio file paths or single audio file path.
        output_dir: The directory where the subtitle file will be saved.
        script_path: Path to the script.json file for language detection (optional).

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
        
        for i, audio_file in enumerate(audio_files):
            if not os.path.exists(audio_file):
                print(f"     - Aviso: Arquivo não encontrado: {audio_file}")
                continue
                
            print(f"     - Processando arquivo {i+1}/{len(audio_files)}: {os.path.basename(audio_file)}")
            
            # Gerar legendas para este arquivo
            subtitle_content = client.generate_subtitles(audio_file, language=detected_language)
            
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