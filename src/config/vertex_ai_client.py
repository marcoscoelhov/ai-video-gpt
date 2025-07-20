"""Cliente principal para geração de imagens com Google Imagen 3 via Vertex AI.

Este módulo fornece uma interface unificada para gerar imagens usando o
Google Imagen 3 através do Vertex AI, com fallback para Gemini 2.0 Flash.

Exemplo de uso:
    from vertex_ai_client import VertexAIImagenClient
    
    # Inicializar o cliente
    client = VertexAIImagenClient()
    
    # Gerar uma imagem
    result = client.generate_image(
        prompt="Um gato astronauta dirigindo um buggy lunar",
        output_path="imagem_gerada.png"
    )
    
    print(f"Imagem salva em: {result['saved_path']}")
"""

import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, List, Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google.cloud import aiplatform
    from vertexai.preview.vision_models import ImageGenerationModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    print("⚠️ Vertex AI não disponível. Usando apenas Gemini como fallback.")

# Importar cliente Gemini como fallback
try:
    from .gemini_imagen_client import GeminiImagenClient
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Cliente Gemini não disponível.")


class VertexAIImagenClient:
    """Cliente principal para geração de imagens com Imagen 3 via Vertex AI.
    
    Esta classe oferece uma interface unificada para gerar imagens usando
    o Google Imagen 3 através do Vertex AI, com fallback automático para
    o Gemini 2.0 Flash em caso de falha.
    
    Attributes:
        project_id (str): ID do projeto Google Cloud.
        location (str): Região do Vertex AI.
        model: Modelo Imagen 3 carregado.
        gemini_client: Cliente Gemini para fallback.
        use_vertex_ai (bool): Se deve usar Vertex AI como principal.
    """
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        gemini_api_key: Optional[str] = None,
        use_vertex_ai_primary: bool = True
    ):
        """Inicializa o cliente Vertex AI com fallback para Gemini.
        
        Args:
            project_id (Optional[str]): ID do projeto Google Cloud.
                                      Se não fornecido, obtém de GOOGLE_CLOUD_PROJECT.
            location (str): Região do Vertex AI. Padrão: "us-central1".
            gemini_api_key (Optional[str]): Chave da API Gemini para fallback.
                                          Se não fornecida, obtém de GEMINI_API_KEY.
            use_vertex_ai_primary (bool): Se deve usar Vertex AI como principal.
        
        Raises:
            ValueError: Se nem Vertex AI nem Gemini estiverem disponíveis.
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = location
        self.model = None
        self.gemini_client = None
        self.use_vertex_ai = use_vertex_ai_primary and VERTEX_AI_AVAILABLE
        
        # Inicializar Vertex AI se disponível e solicitado
        if self.use_vertex_ai and self.project_id:
            try:
                aiplatform.init(project=self.project_id, location=self.location)
                self.model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
                print(f"✅ Vertex AI Imagen 3 inicializado - Projeto: {self.project_id}")
            except Exception as e:
                print(f"⚠️ Falha ao inicializar Vertex AI: {e}")
                self.use_vertex_ai = False
        
        # Inicializar cliente Gemini como fallback
        if GEMINI_AVAILABLE:
            try:
                self.gemini_client = GeminiImagenClient(api_key=gemini_api_key)
                print("✅ Cliente Gemini inicializado como fallback")
            except Exception as e:
                print(f"⚠️ Falha ao inicializar cliente Gemini: {e}")
        
        # Verificar se pelo menos um cliente está disponível
        if not self.use_vertex_ai and not self.gemini_client:
            raise ValueError(
                "Nem Vertex AI nem Gemini estão disponíveis. "
                "Verifique as configurações e dependências."
            )
    
    def generate_image(
        self,
        prompt: str,
        output_path: Optional[Union[str, Path]] = None,
        aspect_ratio: str = "1:1",
        safety_filter_level: str = "block_some",
        person_generation: str = "allow_adult",
        include_text_response: bool = False
    ) -> Dict[str, Any]:
        """Gera uma imagem usando Vertex AI ou Gemini como fallback.
        
        Args:
            prompt (str): Descrição da imagem a ser gerada.
            output_path (Optional[Union[str, Path]]): Caminho onde salvar a imagem.
            aspect_ratio (str): Proporção da imagem (apenas Vertex AI).
            safety_filter_level (str): Nível do filtro de segurança (apenas Vertex AI).
            person_generation (str): Configuração de geração de pessoas (apenas Vertex AI).
            include_text_response (bool): Se deve incluir resposta de texto (apenas Gemini).
        
        Returns:
            Dict[str, Any]: Dicionário contendo:
                - 'success': Se a geração foi bem-sucedida
                - 'image': Objeto da imagem gerada (se aplicável)
                - 'saved_path': Caminho onde a imagem foi salva
                - 'model_used': Modelo usado ('vertex_ai' ou 'gemini')
                - 'text_response': Resposta de texto (apenas Gemini)
                - 'error': Mensagem de erro (se houver)
        """
        # Tentar Vertex AI primeiro se disponível
        if self.use_vertex_ai and self.model:
            try:
                return self._generate_with_vertex_ai(
                    prompt, output_path, aspect_ratio, 
                    safety_filter_level, person_generation
                )
            except Exception as e:
                print(f"⚠️ Falha no Vertex AI, tentando Gemini: {e}")
        
        # Fallback para Gemini
        if self.gemini_client:
            try:
                return self._generate_with_gemini(
                    prompt, output_path, include_text_response
                )
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Falha em ambos os modelos. Último erro: {e}",
                    'model_used': 'none'
                }
        
        return {
            'success': False,
            'error': "Nenhum modelo disponível para geração de imagens",
            'model_used': 'none'
        }
    
    def _generate_with_vertex_ai(
        self,
        prompt: str,
        output_path: Optional[Union[str, Path]],
        aspect_ratio: str,
        safety_filter_level: str,
        person_generation: str
    ) -> Dict[str, Any]:
        """Gera imagem usando Vertex AI Imagen 3."""
        print(f"🎨 Gerando com Vertex AI Imagen 3: {prompt[:50]}...")
        
        # Gerar imagem
        response = self.model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio=aspect_ratio,
            safety_filter_level=safety_filter_level,
            person_generation=person_generation
        )
        
        if not response.images:
            raise Exception("Nenhuma imagem foi gerada pelo Vertex AI")
        
        image = response.images[0]
        saved_path = None
        
        # Salvar se caminho fornecido
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(location=str(output_path))
            saved_path = str(output_path)
            print(f"💾 Imagem salva: {saved_path}")
        
        return {
            'success': True,
            'image': image,
            'saved_path': saved_path,
            'model_used': 'vertex_ai',
            'prompt': prompt,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_with_gemini(
        self,
        prompt: str,
        output_path: Optional[Union[str, Path]],
        include_text_response: bool
    ) -> Dict[str, Any]:
        """Gera imagem usando Gemini 2.0 Flash."""
        print(f"🎨 Gerando com Gemini 2.0 Flash: {prompt[:50]}...")
        
        result = self.gemini_client.generate_image(
            prompt=prompt,
            output_path=output_path,
            include_text_response=include_text_response
        )
        
        return {
            'success': True,
            'image': result.get('image'),
            'saved_path': result.get('saved_path'),
            'text_response': result.get('text_response'),
            'model_used': 'gemini',
            'prompt': prompt,
            'timestamp': datetime.now().isoformat()
        }
    
    async def generate_image_async(
        self,
        prompt: str,
        output_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Versão assíncrona da geração de imagem."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.generate_image,
            prompt,
            output_path,
            **kwargs
        )
    
    def generate_multiple_images(
        self,
        prompts: List[str],
        output_dir: Optional[Union[str, Path]] = None,
        filename_prefix: str = "imagen",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Gera múltiplas imagens a partir de uma lista de prompts."""
        results = []
        
        for i, prompt in enumerate(prompts):
            output_path = None
            if output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{filename_prefix}_{timestamp}_{i+1:03d}.png"
                output_path = output_dir / filename
            
            result = self.generate_image(
                prompt=prompt,
                output_path=output_path,
                **kwargs
            )
            result['index'] = i
            results.append(result)
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre os modelos disponíveis."""
        return {
            'vertex_ai_available': self.use_vertex_ai,
            'gemini_available': self.gemini_client is not None,
            'primary_model': 'vertex_ai' if self.use_vertex_ai else 'gemini',
            'project_id': self.project_id,
            'location': self.location
        }


def test_vertex_ai_client():
    """Testa o funcionamento do cliente Vertex AI."""
    print("🧪 Testando VertexAIImagenClient...")
    
    try:
        # Inicializar cliente
        client = VertexAIImagenClient()
        
        # Mostrar informações do modelo
        info = client.get_model_info()
        print(f"📊 Informações do modelo: {info}")
        
        # Teste de geração
        prompt_teste = "A futuristic robot cat in a cyberpunk city, digital art style"
        
        result = client.generate_image(
            prompt=prompt_teste,
            output_path="teste_vertex_ai_client.png"
        )
        
        if result['success']:
            print(f"✅ Teste bem-sucedido! Modelo usado: {result['model_used']}")
            if result['saved_path']:
                print(f"💾 Imagem salva: {result['saved_path']}")
        else:
            print(f"❌ Teste falhou: {result['error']}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")


if __name__ == "__main__":
    test_vertex_ai_client()