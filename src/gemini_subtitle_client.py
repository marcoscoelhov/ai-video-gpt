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
            prompt = self._create_subtitle_prompt(language)
            
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
    
    def _create_subtitle_prompt(self, language: str) -> str:
        """Cria o prompt otimizado para geração de legendas.
        
        Args:
            language: Idioma de destino
        
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
        
        # Validar formato SRT básico
        if not self._validate_srt_format(cleaned_text):
            print("⚠️ Aviso: Formato SRT pode estar incorreto")
        
        return cleaned_text
    
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