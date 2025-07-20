import os
import json
import re
from typing import List, Dict, Tuple, Optional
from moviepy import AudioFileClip
from .subtitle_styles import SubtitleStyleManager, SubtitleStyle

class ScriptSubtitleSynchronizer:
    """
    Classe para sincronizar legendas com roteiro existente, sem necessidade de transcrição.
    Usa a duração real do áudio gerado pela ElevenLabs para calcular timing preciso.
    """
    
    def __init__(self, style_manager=None):
        self.style_manager = style_manager or SubtitleStyleManager()
        self.default_chars_per_second = 17  # Velocidade de leitura confortável
        self.min_subtitle_duration = 1.0    # Duração mínima em segundos
        self.max_subtitle_duration = 6.0    # Duração máxima em segundos
        self.gap_between_subtitles = 0.1    # Intervalo entre legendas
        
        # Pausas baseadas em pontuação (em segundos)
        self.punctuation_pauses = {
            '.': 0.4,   # Ponto final
            '!': 0.4,   # Exclamação
            '?': 0.4,   # Interrogação
            ',': 0.2,   # Vírgula
            ';': 0.3,   # Ponto e vírgula
            ':': 0.3,   # Dois pontos
            '-': 0.2,   # Hífen/travessão
            '...': 0.5, # Reticências
        }
    
    def get_audio_duration(self, audio_path: str) -> float:
        """
        Obtém a duração de um arquivo de áudio usando MoviePy.
        Suporta arquivos mock para testes.
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            
        Returns:
            Duração em segundos
        """
        try:
            # Verificar se é um arquivo mock
            if os.path.exists(audio_path):
                with open(audio_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line == "MOCK AUDIO FILE":
                        # É um arquivo mock, procurar pela linha de duração
                        for line in f:
                            if line.startswith("Duration:"):
                                duration_str = line.split(":")[1].strip()
                                return float(duration_str.replace("s", ""))
                            
                            # Tentar extrair dos metadados JSON
                            if "duration_seconds" in line:
                                try:
                                    import json
                                    metadata = json.loads(line)
                                    if "duration_seconds" in metadata:
                                        return float(metadata["duration_seconds"])
                                except:
                                    pass
            
            # Se não for mock ou não conseguir extrair a duração, usar MoviePy
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            audio_clip.close()
            return duration
        except Exception as e:
            print(f"Erro ao obter duração do áudio {audio_path}: {e}")
            # Fallback: estimar duração baseada no nome do arquivo
            try:
                filename = os.path.basename(audio_path)
                if "_" in filename and "." in filename:
                    # Tentar extrair texto do nome do arquivo
                    text = filename.split("_")[1].split(".")[0]
                    # Estimar ~0.5s por palavra
                    return len(text.split()) * 0.5
            except:
                pass
            return 0.0
    
    def calculate_speech_rate(self, text: str, audio_duration: float) -> float:
        """
        Calcula a velocidade de fala em caracteres por segundo.
        
        Args:
            text: Texto da cena
            audio_duration: Duração do áudio em segundos
            
        Returns:
            Velocidade em caracteres por segundo
        """
        if audio_duration <= 0:
            return self.default_chars_per_second
        
        # Contar apenas caracteres visíveis (sem espaços extras)
        clean_text = re.sub(r'\s+', ' ', text.strip())
        char_count = len(clean_text)
        
        if char_count == 0:
            return self.default_chars_per_second
        
        speech_rate = char_count / audio_duration
        
        # Limitar velocidade a valores mais realistas (12-25 chars/sec)
        speech_rate = max(12, min(25, speech_rate))
        
        return speech_rate
    
    def split_text_into_sentences(self, text: str) -> List[str]:
        """
        Divide o texto em frases baseado na pontuação.
        
        Args:
            text: Texto para dividir
            
        Returns:
            Lista de frases
        """
        # Padrão para dividir em frases (ponto, exclamação, interrogação)
        sentence_pattern = r'[.!?]+\s*'
        sentences = re.split(sentence_pattern, text)
        
        # Remover frases vazias e limpar espaços
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def calculate_pause_duration(self, text: str) -> float:
        """
        Calcula a duração total de pausas baseada na pontuação.
        
        Args:
            text: Texto para analisar
            
        Returns:
            Duração total de pausas em segundos
        """
        total_pause = 0.0
        
        # Pausas ajustadas para melhor precisão
        adjusted_pauses = {
            '.': 0.3,   # Ponto final (reduzido)
            '!': 0.25,  # Exclamação (reduzido)
            '?': 0.25,  # Interrogação (reduzido)
            ',': 0.1,   # Vírgula (reduzido)
            ';': 0.2,   # Ponto e vírgula (reduzido)
            ':': 0.2,   # Dois pontos (reduzido)
            '-': 0.15,  # Hífen/travessão (reduzido)
            '...': 0.4, # Reticências (reduzido)
        }
        
        for punct, pause_duration in adjusted_pauses.items():
            count = text.count(punct)
            total_pause += count * pause_duration
        
        return total_pause
    
    def distribute_timing_intelligent(self, text: str, total_duration: float, 
                                    speech_rate: float) -> List[Dict]:
        """
        Distribui timing considerando pontuação, pausas naturais e velocidade de fala.
        
        Args:
            text: Texto da cena
            total_duration: Duração total disponível
            speech_rate: Velocidade de fala em chars/segundo
            
        Returns:
            Lista de dicionários com timing e texto de cada legenda
        """
        sentences = self.split_text_into_sentences(text)
        
        if not sentences:
            return [{
                'text': text,
                'start_time': 0.0,
                'end_time': total_duration,
                'duration': total_duration
            }]
        
        # Calcular duração base para cada frase
        sentence_data = []
        total_base_duration = 0
        
        for sentence in sentences:
            char_count = len(sentence)
            
            # Duração baseada na velocidade da fala
            speech_duration = char_count / speech_rate
            
            # Adicionar pausas específicas da frase
            pause_duration = self.calculate_pause_duration(sentence)
            
            # Duração total da frase
            base_duration = speech_duration + pause_duration
            
            sentence_data.append({
                'text': sentence.strip(),
                'char_count': char_count,
                'base_duration': base_duration,
                'pause_duration': pause_duration
            })
            
            total_base_duration += base_duration
        
        # Calcular fator de escala para ajustar ao tempo total
        if total_base_duration > 0:
            scale_factor = total_duration / total_base_duration
        else:
            scale_factor = 1.0
        
        # Aplicar escala e gerar timing final
        timing_data = []
        current_time = 0.0
        
        for data in sentence_data:
            # Aplicar fator de escala
            duration = data['base_duration'] * scale_factor
            
            # Garantir limites razoáveis
            duration = max(self.min_subtitle_duration, 
                          min(self.max_subtitle_duration, duration))
            
            timing_data.append({
                'text': data['text'],
                'start_time': current_time,
                'end_time': current_time + duration,
                'duration': duration
            })
            
            current_time += duration
        
        return timing_data
    
    def sync_script_with_audio(self, script_data: Dict, audio_files: List[str]) -> List[Dict]:
        """
        Sincroniza roteiro com arquivos de áudio.
        
        Args:
            script_data: Dados do roteiro JSON
            audio_files: Lista de arquivos de áudio
            
        Returns:
            Lista de dados sincronizados por cena
        """
        scenes = script_data.get('scenes', [])
        
        if len(scenes) != len(audio_files):
            print(f"⚠️ Aviso: {len(scenes)} cenas no roteiro, {len(audio_files)} arquivos de áudio")
        
        synchronized_data = []
        cumulative_time = 0.0
        
        for i, (scene, audio_file) in enumerate(zip(scenes, audio_files)):
            if not os.path.exists(audio_file):
                print(f"⚠️ Arquivo de áudio não encontrado: {audio_file}")
                continue
            
            # Obter texto da cena (campo 'narration' no script.json)
            scene_text = scene.get('narration', scene.get('text', '')).strip()
            if not scene_text:
                print(f"⚠️ Texto vazio na cena {i+1}")
                continue
            
            # Obter duração real do áudio
            audio_duration = self.get_audio_duration(audio_file)
            if audio_duration <= 0:
                print(f"⚠️ Duração inválida para {audio_file}")
                continue
            
            # Calcular velocidade de fala
            speech_rate = self.calculate_speech_rate(scene_text, audio_duration)
            
            # Distribuir timing inteligente
            timing_data = self.distribute_timing_intelligent(
                scene_text, audio_duration, speech_rate
            )
            
            # Ajustar timing com offset acumulado
            for item in timing_data:
                item['start_time'] += cumulative_time
                item['end_time'] += cumulative_time
                item['scene_index'] = i + 1
                item['audio_file'] = audio_file
            
            synchronized_data.extend(timing_data)
            cumulative_time += audio_duration + 0.5  # 0.5s gap entre cenas
            
            print(f"✅ Cena {i+1}: {len(timing_data)} legendas, duração {audio_duration:.1f}s")
        
        return synchronized_data
    
    def generate_srt_from_sync_data(self, sync_data: List[Dict]) -> str:
        """
        Gera conteúdo SRT a partir dos dados sincronizados.
        
        Args:
            sync_data: Dados sincronizados
            
        Returns:
            Conteúdo SRT formatado
        """
        srt_lines = []
        
        for i, item in enumerate(sync_data, 1):
            # Número da legenda
            srt_lines.append(str(i))
            
            # Timestamp
            start_time = self.seconds_to_srt_time(item['start_time'])
            end_time = self.seconds_to_srt_time(item['end_time'])
            srt_lines.append(f"{start_time} --> {end_time}")
            
            # Texto
            srt_lines.append(item['text'])
            
            # Linha vazia
            srt_lines.append("")
        
        return "\n".join(srt_lines)
    
    def seconds_to_srt_time(self, seconds: float) -> str:
        """
        Converte segundos para formato de tempo SRT (HH:MM:SS,mmm).
        
        Args:
            seconds: Tempo em segundos
            
        Returns:
            String formatada no padrão SRT
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def generate_subtitles_from_script(self, script_path: str, audio_files: List[str], 
                                     output_dir: str, style_name: str = "modern") -> str:
        """
        Função principal para gerar legendas a partir do roteiro existente.
        
        Args:
            script_path: Caminho para o arquivo script.json
            audio_files: Lista de arquivos de áudio
            output_dir: Diretório de saída
            style_name: Nome do estilo de legenda
            
        Returns:
            Caminho do arquivo SRT gerado
        """
        print(f"🎬 Gerando legendas a partir do roteiro...")
        print(f"📄 Roteiro: {os.path.basename(script_path)}")
        print(f"🎵 Arquivos de áudio: {len(audio_files)}")
        print(f"🎨 Estilo: {style_name}")
        
        # Criar diretório de saída
        os.makedirs(output_dir, exist_ok=True)
        
        # Carregar roteiro
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                script_data = json.load(f)
        except Exception as e:
            raise Exception(f"Erro ao carregar roteiro: {e}")
        
        # Sincronizar com áudio
        sync_data = self.sync_script_with_audio(script_data, audio_files)
        
        if not sync_data:
            raise Exception("Nenhum dado sincronizado gerado")
        
        # Gerar conteúdo SRT
        srt_content = self.generate_srt_from_sync_data(sync_data)
        
        # Salvar arquivo
        output_path = os.path.join(output_dir, "subtitles.srt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        print(f"✅ Legendas geradas: {output_path}")
        print(f"📊 Total de legendas: {len(sync_data)}")
        
        # Calcular estatísticas
        total_duration = max(item['end_time'] for item in sync_data) if sync_data else 0
        avg_duration = sum(item['duration'] for item in sync_data) / len(sync_data) if sync_data else 0
        
        print(f"⏱️ Duração total: {total_duration:.1f}s")
        print(f"📏 Duração média por legenda: {avg_duration:.1f}s")
        print(f"💰 Custo: $0.00 (sem transcrição!)")
        
        return output_path

# Função de conveniência para uso direto
def generate_subtitles_from_script(script_path: str, audio_files: List[str], 
                                 output_dir: str, style_name: str = "modern") -> str:
    """
    Função de conveniência para gerar legendas a partir do roteiro.
    
    Args:
        script_path: Caminho para o arquivo script.json
        audio_files: Lista de arquivos de áudio
        output_dir: Diretório de saída
        style_name: Nome do estilo de legenda
        
    Returns:
        Caminho do arquivo SRT gerado
    """
    synchronizer = ScriptSubtitleSynchronizer()
    return synchronizer.generate_subtitles_from_script(
        script_path, audio_files, output_dir, style_name
    )

if __name__ == "__main__":
    # Exemplo de uso para testes
    print("🧪 Testando sincronização de legendas com roteiro...")
    
    # Exemplo de dados de teste
    test_script = {
        "scenes": [
            {"text": "Olá! Bem-vindos ao nosso vídeo sobre inteligência artificial."},
            {"text": "Hoje vamos explorar como a IA está transformando o mundo."},
            {"text": "Obrigado por assistir! Não esqueçam de se inscrever no canal."}
        ]
    }
    
    # Simular arquivos de áudio (substitua por caminhos reais)
    test_audio_files = [
        "audio/scene_1.mp3",
        "audio/scene_2.mp3", 
        "audio/scene_3.mp3"
    ]
    
    synchronizer = ScriptSubtitleSynchronizer()
    
    # Testar distribuição de timing
    test_text = "Olá! Bem-vindos ao nosso vídeo. Hoje vamos aprender sobre IA."
    timing_data = synchronizer.distribute_timing_intelligent(test_text, 10.0, 15.0)
    
    print("\n📋 Resultado do teste de timing:")
    for i, item in enumerate(timing_data, 1):
        print(f"  {i}. {item['start_time']:.1f}s - {item['end_time']:.1f}s: '{item['text']}'")
    
    print("\n✅ Teste concluído com sucesso!")