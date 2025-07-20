"""Cliente para integração com ElevenLabs API."""
import os
import requests
from typing import Optional, Dict, List
from elevenlabs import ElevenLabs
from .voice_config import (
    ELEVENLABS_DEFAULT_SETTINGS,
    get_voice_id,
    detect_language_from_text
)

class ElevenLabsClient:
    """Cliente para comunicação com a API do ElevenLabs."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o cliente ElevenLabs.
        
        Args:
            api_key (str, optional): Chave da API. Se não fornecida, busca em ELEVENLABS_API_KEY
        """
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "API key do ElevenLabs não encontrada. "
                "Defina ELEVENLABS_API_KEY como variável de ambiente ou passe como parâmetro."
            )
        
        # Inicializar cliente ElevenLabs
        self.client = ElevenLabs(api_key=self.api_key)
        
        # Cache de vozes disponíveis
        self._voices_cache: Optional[List[Dict]] = None
    
    def is_available(self) -> bool:
        """
        Verifica se o ElevenLabs está disponível e funcionando.
        
        Returns:
            bool: True se disponível, False caso contrário
        """
        try:
            # Tenta fazer uma requisição simples para verificar conectividade
            response = requests.get(
                "https://api.elevenlabs.io/v1/voices",
                headers={"xi-api-key": self.api_key},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"ElevenLabs não disponível: {e}")
            return False
    
    def get_available_voices(self, force_refresh: bool = False) -> List[Dict]:
        """
        Obtém lista de vozes disponíveis.
        
        Args:
            force_refresh (bool): Forçar atualização do cache
        
        Returns:
            List[Dict]: Lista de vozes disponíveis
        """
        if self._voices_cache is None or force_refresh:
            try:
                voices = self.client.voices.get_all()
                self._voices_cache = [{
                    'voice_id': voice.voice_id,
                    'name': voice.name,
                    'category': getattr(voice, 'category', 'unknown'),
                    'labels': getattr(voice, 'labels', {})
                } for voice in voices.voices]
            except Exception as e:
                print(f"Erro ao conectar com ElevenLabs: {e}")
                self._voices_cache = []
        
        return self._voices_cache or []
    
    def generate_audio(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: Optional[str] = None,
        voice_type: str = 'default',
        settings: Optional[Dict] = None
    ) -> bytes:
        """
        Gera áudio usando ElevenLabs.
        
        Args:
            text (str): Texto para converter em áudio
            voice_id (str, optional): ID específico da voz
            language (str, optional): Idioma (auto-detectado se não fornecido)
            voice_type (str): Tipo de voz ('default', 'male', 'female', 'narrator')
            settings (dict, optional): Configurações customizadas
        
        Returns:
            bytes: Dados do áudio gerado
        
        Raises:
            Exception: Se houver erro na geração
        """
        try:
            # Detectar idioma se não fornecido
            if not language:
                language = detect_language_from_text(text)
            
            # Obter ID da voz
            if not voice_id:
                voice_id = get_voice_id(language, voice_type)
            
            # Configurações de voz
            voice_settings = ELEVENLABS_DEFAULT_SETTINGS.copy()
            if settings:
                voice_settings.update(settings)
            
            print(f"  -> Gerando áudio com ElevenLabs (voz: {voice_id}, idioma: {language})")
            
            # Gerar áudio usando a nova API
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",  # Modelo multilíngue
                voice_settings={
                    'stability': voice_settings['stability'],
                    'similarity_boost': voice_settings['similarity_boost'],
                    'style': voice_settings.get('style', 0.0),
                    'use_speaker_boost': voice_settings.get('use_speaker_boost', True)
                }
            )
            
            # Converter generator para bytes
            audio_data = b''.join(audio_generator)
            return audio_data
            
        except Exception as e:
            print(f"Erro ao gerar áudio com ElevenLabs: {e}")
            raise
    
    def save_audio(
        self,
        text: str,
        output_path: str,
        voice_id: Optional[str] = None,
        language: Optional[str] = None,
        voice_type: str = 'default',
        settings: Optional[Dict] = None
    ) -> bool:
        """
        Gera e salva áudio em arquivo.
        
        Args:
            text (str): Texto para converter
            output_path (str): Caminho do arquivo de saída
            voice_id (str, optional): ID específico da voz
            language (str, optional): Idioma
            voice_type (str): Tipo de voz
            settings (dict, optional): Configurações customizadas
        
        Returns:
            bool: True se sucesso, False caso contrário
        """
        try:
            audio_data = self.generate_audio(
                text=text,
                voice_id=voice_id,
                language=language,
                voice_type=voice_type,
                settings=settings
            )
            
            # Salvar arquivo
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            print(f"     - Áudio ElevenLabs salvo em: {output_path}")
            return True
            
        except Exception as e:
            print(f"     - Erro ao salvar áudio ElevenLabs: {e}")
            return False
    
    def get_voice_info(self, voice_id: str) -> Optional[Dict]:
        """
        Obtém informações sobre uma voz específica.
        
        Args:
            voice_id (str): ID da voz
        
        Returns:
            Dict: Informações da voz ou None se não encontrada
        """
        voices = self.get_available_voices()
        
        for voice in voices:
            if voice.get('voice_id') == voice_id:
                return voice
        
        return None
    
    def list_voices_by_language(self, language: str = 'pt-br') -> List[Dict]:
        """
        Lista vozes disponíveis para um idioma específico.
        
        Args:
            language (str): Código do idioma
        
        Returns:
            List[Dict]: Lista de vozes para o idioma
        """
        all_voices = self.get_available_voices()
        
        # Filtrar por idioma (se a informação estiver disponível)
        # Nota: A API do ElevenLabs nem sempre fornece informação de idioma
        # então retornamos todas as vozes disponíveis
        return all_voices

# Função de conveniência para uso direto
def create_elevenlabs_client() -> Optional[ElevenLabsClient]:
    """
    Cria um cliente ElevenLabs se a API key estiver disponível.
    
    Returns:
        ElevenLabsClient ou None se não disponível
    """
    try:
        return ElevenLabsClient()
    except ValueError:
        return None

if __name__ == '__main__':
    # Teste básico do cliente
    try:
        client = ElevenLabsClient()
        
        if client.is_available():
            print("✅ ElevenLabs disponível")
            
            # Listar vozes
            voices = client.get_available_voices()
            print(f"📢 Vozes disponíveis: {len(voices)}")
            
            for voice in voices[:3]:  # Mostrar apenas as 3 primeiras
                print(f"  - {voice.get('name', 'N/A')} (ID: {voice.get('voice_id', 'N/A')})")
        else:
            print("❌ ElevenLabs não disponível")
            
    except Exception as e:
        print(f"❌ Erro ao testar ElevenLabs: {e}")