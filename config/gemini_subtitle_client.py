"""Cliente para geração de legendas usando Google Gemini 2.0 Flash."""

import os
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class GeminiSubtitleClient:
    """Cliente para geração de legendas usando Google Gemini 2.0 Flash."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Inicializa o cliente Gemini para legendas.
        
        Args:
            api_key: Chave da API do Gemini. Se não fornecida, usa GEMINI_API_KEY do ambiente.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não encontrada. Configure no arquivo .env")
        
        # Configurar Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Custo estimado por minuto de áudio (baseado na documentação do Gemini)
        self.cost_per_minute = 0.00025  # $0.00025 por minuto de áudio
    
    def generate_subtitles(self, audio_file_path: str, language: str = "pt-BR") -> str:
        """Gera legendas SRT a partir de um arquivo de áudio.
        
        Args:
            audio_file_path: Caminho para o arquivo de áudio
            language: Idioma para transcrição (padrão: pt-BR)
        
        Returns:
            Conteúdo das legendas no formato SRT
        
        Raises:
            FileNotFoundError: Se o arquivo de áudio não existir
            Exception: Se houver erro na transcrição
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_file_path}")
        
        try:
            print(f"🎵 Gerando legendas para: {audio_file_path}")
            
            # Upload do arquivo de áudio
            audio_upload = genai.upload_file(audio_file_path)
            print(f"✅ Arquivo enviado: {audio_upload.name}")
            
            # Prompt otimizado para geração de legendas SRT
            prompt = self._create_subtitle_prompt(language, "srt")
            
            # Gerar transcrição
            response = self.model.generate_content([prompt, audio_upload])
            
            # Limpar arquivo temporário
            genai.delete_file(audio_upload.name)
            
            # Processar e validar a resposta
            subtitle_content = self._process_subtitle_response(response.text)
            
            print(f"✅ Legendas geradas com sucesso")
            return subtitle_content
            
        except Exception as e:
            print(f"❌ Erro ao gerar legendas: {e}")
            raise
    
    def generate_subtitles_json(self, audio_file_path: str, language: str = "pt-BR") -> dict:
        """Gera legendas em formato JSON a partir de um arquivo de áudio.
        
        Args:
            audio_file_path: Caminho para o arquivo de áudio
            language: Idioma para transcrição (padrão: pt-BR)
        
        Returns:
            Dicionário com legendas estruturadas em JSON
        
        Raises:
            FileNotFoundError: Se o arquivo de áudio não existir
            Exception: Se houver erro na transcrição
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_file_path}")
        
        try:
            print(f"🎵 Gerando legendas JSON para: {audio_file_path}")
            
            # Upload do arquivo de áudio
            audio_upload = genai.upload_file(audio_file_path)
            print(f"✅ Arquivo enviado: {audio_upload.name}")
            
            # Prompt otimizado para geração de legendas JSON
            prompt = self._create_subtitle_prompt(language, "json")
            
            # Gerar transcrição
            response = self.model.generate_content([prompt, audio_upload])
            
            # Limpar arquivo temporário
            genai.delete_file(audio_upload.name)
            
            # Processar e validar a resposta JSON
            subtitle_json = self._process_json_response(response.text)
            
            print(f"✅ Legendas JSON geradas com sucesso")
            return subtitle_json
            
        except Exception as e:
            print(f"❌ Erro ao gerar legendas JSON: {e}")
            raise
    
    def generate_subtitles_from_multiple_files(self, audio_files: List[str], 
                                             language: str = "pt-BR") -> List[str]:
        """Gera legendas para múltiplos arquivos de áudio.
        
        Args:
            audio_files: Lista de caminhos para arquivos de áudio
            language: Idioma para transcrição
        
        Returns:
            Lista com conteúdo das legendas no formato SRT
        """
        subtitles = []
        
        for i, audio_file in enumerate(audio_files, 1):
            print(f"\n📝 Processando arquivo {i}/{len(audio_files)}: {Path(audio_file).name}")
            try:
                subtitle = self.generate_subtitles(audio_file, language)
                subtitles.append(subtitle)
            except Exception as e:
                print(f"❌ Erro no arquivo {audio_file}: {e}")
                # Adicionar legenda vazia em caso de erro
                subtitles.append("")
        
        return subtitles
    
    def _create_subtitle_prompt(self, language: str, output_format: str = "srt") -> str:
        """Cria o prompt otimizado para geração de legendas.
        
        Args:
            language: Idioma de destino
            output_format: Formato de saída ('srt' ou 'json')
        
        Returns:
            Prompt formatado
        """
        language_map = {
            "pt-BR": "português brasileiro",
            "en": "inglês",
            "es": "espanhol",
            "fr": "francês",
            "de": "alemão",
            "it": "italiano"
        }
        
        target_language = language_map.get(language, "português brasileiro")
        
        if output_format == "json":
            return f"""
Transcreva este áudio em {target_language} e formate como JSON estruturado.

REQUISITOS IMPORTANTES:
1. Retorne um JSON válido com a estrutura especificada
2. Timestamps no formato: HH:MM:SS.mmm
3. Máximo 2 linhas por legenda (use \n para quebra de linha)
4. Máximo 42 caracteres por linha
5. Duração mínima de 1 segundo por legenda
6. Seja preciso com os timestamps
7. Use pontuação adequada

ESTRUTURA JSON OBRIGATÓRIA:
{{
  "subtitles": [
    {{
      "id": 1,
      "start_time": "00:00:00.000",
      "end_time": "00:00:03.500",
      "text": "Olá, este é um exemplo de legenda."
    }},
    {{
      "id": 2,
      "start_time": "00:00:03.500",
      "end_time": "00:00:07.000",
      "text": "Esta é a segunda legenda."
    }}
  ],
  "metadata": {{
    "language": "{language}",
    "total_duration": "duração_total_do_audio",
    "created_at": "timestamp_atual"
  }}
}}

APENAS retorne o JSON válido, sem explicações adicionais.
"""
        else:
            return f"""
Transcreva este áudio em {target_language} e formate como legendas SRT.

REQUISITOS IMPORTANTES:
1. Use o formato SRT padrão (número, timestamp, texto, linha vazia)
2. Timestamps no formato: HH:MM:SS,mmm --> HH:MM:SS,mmm
3. Máximo 2 linhas por legenda
4. Máximo 42 caracteres por linha
5. Duração mínima de 1 segundo por legenda
6. Seja preciso com os timestamps
7. Use pontuação adequada

EXEMPLO DE FORMATO:
1
00:00:00,000 --> 00:00:03,500
Olá, este é um exemplo
de legenda em duas linhas.

2
00:00:03,500 --> 00:00:07,000
Esta é a segunda legenda.

APENAS retorne o conteúdo SRT, sem explicações adicionais.
"""
    
    def _process_subtitle_response(self, response_text: str) -> str:
        """Processa e valida a resposta do Gemini.
        
        Args:
            response_text: Texto bruto da resposta
        
        Returns:
            Conteúdo SRT processado e validado
        """
        # Remover possíveis marcadores de código
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```"):
            lines = cleaned_text.split("\n")
            # Remover primeira e última linha se forem marcadores
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned_text = "\n".join(lines)
        
        # Tentar corrigir quebras de linha problemáticas no JSON
        # Procurar por padrões como "text": "linha1\nlinha2" e corrigir
        import re
        # Padrão para encontrar texto com quebras de linha dentro de strings JSON
        pattern = r'("text"\s*:\s*")([^"]*?)\n([^"]*?)("[,}])'
        
        def fix_newlines(match):
            prefix = match.group(1)
            text1 = match.group(2)
            text2 = match.group(3)
            suffix = match.group(4)
            # Juntar as linhas com espaço
            combined_text = f"{text1} {text2}".strip()
            return f'{prefix}{combined_text}{suffix}'
        
        cleaned_text = re.sub(pattern, fix_newlines, cleaned_text, flags=re.MULTILINE)
        
        # Validar formato SRT básico
        if not self._validate_srt_format(cleaned_text):
            print("⚠️ Aviso: Formato SRT pode estar incorreto")
        
        # Corrigir problemas de timing
        print("     - Corrigindo sincronização das legendas...")
        corrected_text = self._fix_subtitle_timing(cleaned_text)
        
        return corrected_text
    
    def _validate_srt_format(self, srt_content: str) -> bool:
        """Valida se o conteúdo está no formato SRT.
        
        Args:
            srt_content: Conteúdo a ser validado
        
        Returns:
            True se o formato parecer válido
        """
        lines = srt_content.strip().split("\n")
        
        # Verificar se tem pelo menos uma legenda (mínimo 3 linhas)
        if len(lines) < 3:
            return False
        
        # Verificar se a primeira linha é um número
        try:
            int(lines[0].strip())
        except ValueError:
            return False
        
        # Verificar se a segunda linha tem formato de timestamp
        if "-->" not in lines[1]:
            return False
        
        return True
    
    def _fix_subtitle_timing(self, srt_content: str) -> str:
        """Corrige problemas de timing nas legendas SRT.
        
        Args:
            srt_content: Conteúdo SRT original
        
        Returns:
            Conteúdo SRT com timing corrigido
        """
        lines = srt_content.strip().split("\n")
        subtitles = []
        current_subtitle = {}
        
        # Parse das legendas
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:  # Linha vazia
                if current_subtitle:
                    subtitles.append(current_subtitle)
                    current_subtitle = {}
                i += 1
                continue
            
            if line.isdigit():  # Número da legenda
                current_subtitle["id"] = int(line)
            elif "-->" in line:  # Timestamp
                parts = line.split("-->")
                if len(parts) == 2:
                    current_subtitle["start"] = parts[0].strip()
                    current_subtitle["end"] = parts[1].strip()
            else:  # Texto
                if "text" in current_subtitle:
                    current_subtitle["text"] += "\n" + line
                else:
                    current_subtitle["text"] = line
            
            i += 1
        
        # Adicionar última legenda
        if current_subtitle:
            subtitles.append(current_subtitle)
        
        # Corrigir timing
        def time_to_seconds(time_str):
            """Converte HH:MM:SS,mmm para segundos."""
            try:
                time_str = time_str.replace(",", ".")
                parts = time_str.split(":")
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            except:
                return 0.0
        
        def seconds_to_time(seconds):
            """Converte segundos para HH:MM:SS,mmm."""
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds - int(seconds)) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
        # Corrigir sobreposições e gaps
        for i in range(len(subtitles)):
            if "start" not in subtitles[i] or "end" not in subtitles[i]:
                continue
                
            start_time = time_to_seconds(subtitles[i]["start"])
            end_time = time_to_seconds(subtitles[i]["end"])
            
            # Garantir duração mínima de 1 segundo
            if end_time - start_time < 1.0:
                end_time = start_time + 1.0
            
            # Verificar sobreposição com próxima legenda
            if i + 1 < len(subtitles) and "start" in subtitles[i + 1]:
                next_start = time_to_seconds(subtitles[i + 1]["start"])
                
                # Se há sobreposição, ajustar
                if end_time > next_start:
                    # Deixar gap de 0.1 segundos
                    end_time = next_start - 0.1
                    
                    # Se ficou muito curto, ajustar o início da próxima
                    if end_time - start_time < 1.0:
                        end_time = start_time + 1.0
                        subtitles[i + 1]["start"] = seconds_to_time(end_time + 0.1)
            
            # Atualizar timestamps
            subtitles[i]["start"] = seconds_to_time(start_time)
            subtitles[i]["end"] = seconds_to_time(end_time)
        
        # Reconstruir SRT
        result_lines = []
        for subtitle in subtitles:
            if "id" in subtitle and "start" in subtitle and "end" in subtitle and "text" in subtitle:
                result_lines.append(str(subtitle["id"]))
                result_lines.append(f"{subtitle['start']} --> {subtitle['end']}")
                result_lines.append(subtitle["text"])
                result_lines.append("")  # Linha vazia
        
        return "\n".join(result_lines)
    
    def _process_json_response(self, response_text: str) -> dict:
        """Processa e valida a resposta JSON do Gemini.
        
        Args:
            response_text: Texto bruto da resposta
        
        Returns:
            Dicionário JSON processado e validado
        """
        import json
        from datetime import datetime
        
        # Remover possíveis marcadores de código
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```"):
            lines = cleaned_text.split("\n")
            # Remover primeira e última linha se forem marcadores
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned_text = "\n".join(lines)
        
        try:
            # Limpar caracteres de controle problemáticos
            import re
            # Remover caracteres de controle exceto \n, \r, \t
            cleaned_text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned_text)
            
            # Tentar fazer parse do JSON
            subtitle_json = json.loads(cleaned_text)
            
            # Validar estrutura básica
            if not isinstance(subtitle_json, dict):
                raise ValueError("Resposta não é um objeto JSON válido")
            
            if "subtitles" not in subtitle_json:
                raise ValueError("Campo 'subtitles' não encontrado no JSON")
            
            # Adicionar metadados se não existirem
            if "metadata" not in subtitle_json:
                subtitle_json["metadata"] = {}
            
            # Preencher metadados padrão
            metadata = subtitle_json["metadata"]
            if "created_at" not in metadata:
                metadata["created_at"] = datetime.now().isoformat()
            
            # Validar e limpar legendas
            for i, subtitle in enumerate(subtitle_json["subtitles"]):
                if not all(key in subtitle for key in ["id", "start_time", "end_time", "text"]):
                    print(f"⚠️ Aviso: Legenda {i+1} está incompleta")
                
                # Limpar texto das legendas
                if "text" in subtitle:
                    # Normalizar quebras de linha
                    subtitle["text"] = subtitle["text"].replace("\n", " ").strip()
            
            return subtitle_json
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Erro ao fazer parse do JSON: {e}")
            print(f"Resposta recebida: {cleaned_text[:200]}...")
            # Retornar estrutura mínima em caso de erro
            return {
                "subtitles": [],
                "metadata": {
                    "language": "pt-BR",
                    "error": "Falha no parse do JSON",
                    "created_at": datetime.now().isoformat()
                }
            }
    
    def json_to_srt(self, subtitle_json: dict) -> str:
        """Converte legendas JSON para formato SRT.
        
        Args:
            subtitle_json: Dicionário com legendas em formato JSON
        
        Returns:
            String com legendas no formato SRT
        """
        if not subtitle_json or "subtitles" not in subtitle_json:
            return ""
        
        srt_lines = []
        
        for subtitle in subtitle_json["subtitles"]:
            # Número da legenda
            srt_lines.append(str(subtitle.get("id", 1)))
            
            # Timestamps (converter de HH:MM:SS.mmm para HH:MM:SS,mmm)
            start_time = subtitle.get("start_time", "00:00:00.000").replace(".", ",")
            end_time = subtitle.get("end_time", "00:00:01.000").replace(".", ",")
            srt_lines.append(f"{start_time} --> {end_time}")
            
            # Texto da legenda
            text = subtitle.get("text", "")
            srt_lines.append(text)
            
            # Linha vazia entre legendas
            srt_lines.append("")
        
        return "\n".join(srt_lines)
    
    def srt_to_json(self, srt_content: str, language: str = "pt-BR") -> dict:
        """Converte legendas SRT para formato JSON.
        
        Args:
            srt_content: String com legendas no formato SRT
            language: Idioma das legendas
        
        Returns:
            Dicionário com legendas em formato JSON
        """
        from datetime import datetime
        
        lines = srt_content.strip().split("\n")
        subtitles = []
        current_subtitle = {}
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Linha vazia - finalizar legenda atual
            if not line:
                if current_subtitle:
                    subtitles.append(current_subtitle)
                    current_subtitle = {}
                i += 1
                continue
            
            # Número da legenda
            if line.isdigit():
                current_subtitle["id"] = int(line)
            
            # Timestamp
            elif "-->" in line:
                parts = line.split("-->")
                if len(parts) == 2:
                    start_time = parts[0].strip().replace(",", ".")
                    end_time = parts[1].strip().replace(",", ".")
                    current_subtitle["start_time"] = start_time
                    current_subtitle["end_time"] = end_time
            
            # Texto da legenda
            else:
                if "text" in current_subtitle:
                    current_subtitle["text"] += "\n" + line
                else:
                    current_subtitle["text"] = line
            
            i += 1
        
        # Adicionar última legenda se existir
        if current_subtitle:
            subtitles.append(current_subtitle)
        
        return {
            "subtitles": subtitles,
            "metadata": {
                "language": language,
                "total_duration": subtitles[-1]["end_time"] if subtitles else "00:00:00.000",
                "created_at": datetime.now().isoformat()
            }
        }
    
    def estimate_cost(self, audio_duration_minutes: float) -> float:
        """Estima o custo para transcrição de áudio.
        
        Args:
            audio_duration_minutes: Duração do áudio em minutos
        
        Returns:
            Custo estimado em USD
        """
        return audio_duration_minutes * self.cost_per_minute
    
    def get_supported_formats(self) -> List[str]:
        """Retorna lista de formatos de áudio suportados.
        
        Returns:
            Lista de extensões suportadas
        """
        return ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac']

# Função de conveniência para uso rápido
def generate_subtitles_quick(audio_file_path: str, 
                           output_file_path: Optional[str] = None,
                           language: str = "pt-BR") -> str:
    """Função de conveniência para gerar legendas rapidamente.
    
    Args:
        audio_file_path: Caminho para o arquivo de áudio
        output_file_path: Caminho para salvar as legendas (opcional)
        language: Idioma para transcrição
    
    Returns:
        Conteúdo das legendas SRT
    """
    client = GeminiSubtitleClient()
    subtitles = client.generate_subtitles(audio_file_path, language)
    
    if output_file_path:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(subtitles)
        print(f"💾 Legendas salvas em: {output_file_path}")
    
    return subtitles

if __name__ == "__main__":
    # Exemplo de uso
    print("🧪 Teste da GeminiSubtitleClient")
    
    # Verificar se existe arquivo de áudio para teste
    test_audio = "output/video_um_robô_explorando_uma_cidade_futurística_20250715_201003/audio/audio_scene_01.mp3"
    
    if os.path.exists(test_audio):
        try:
            subtitles = generate_subtitles_quick(
                test_audio, 
                "test_gemini_subtitles.srt"
            )
            print("\n📝 Primeiras linhas das legendas:")
            print(subtitles[:200] + "...")
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
    else:
        print(f"❌ Arquivo de teste não encontrado: {test_audio}")