"""Testes básicos para a classe GeminiImagenClient.

Este arquivo contém testes unitários e de integração para validar
a funcionalidade da classe GeminiImagenClient.
"""

import os
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

# Importar a classe a ser testada
from gemini_imagen_client import GeminiImagenClient, generate_image_quick


class TestGeminiImagenClient:
    """Testes para a classe GeminiImagenClient."""
    
    def setup_method(self):
        """Configuração executada antes de cada teste."""
        self.api_key = "test_api_key_123"
        self.test_prompt = "Um gato astronauta dirigindo um buggy lunar"
        
    def test_init_with_api_key(self):
        """Testa inicialização com API key fornecida."""
        client = GeminiImagenClient(api_key=self.api_key)
        assert client.model_name == "gemini-2.0-flash-exp"
        
    def test_init_without_api_key_raises_error(self):
        """Testa que inicialização sem API key levanta erro."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key não fornecida"):
                GeminiImagenClient()
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'env_api_key'})
    def test_init_with_env_api_key(self):
        """Testa inicialização com API key da variável de ambiente."""
        client = GeminiImagenClient()
        # Verificar que não levanta erro
        assert client.model_name == "gemini-2.0-flash-exp"
    
    def test_custom_model_name(self):
        """Testa inicialização com nome de modelo customizado."""
        custom_model = "gemini-custom-model"
        client = GeminiImagenClient(api_key=self.api_key, model_name=custom_model)
        assert client.model_name == custom_model
    
    @patch('gemini_imagen_client.genai.Client')
    @patch('gemini_imagen_client.Image')
    def test_generate_image_success(self, mock_image, mock_client):
        """Testa geração bem-sucedida de imagem."""
        # Configurar mocks
        mock_response = Mock()
        mock_part = Mock()
        mock_part.text = "Imagem gerada com sucesso"
        mock_part.inline_data = Mock()
        mock_part.inline_data.data = b"fake_image_data"
        mock_response.candidates = [Mock()]
        mock_response.candidates[0].content.parts = [mock_part]
        
        mock_client_instance = Mock()
        mock_client_instance.models.generate_content.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        mock_pil_image = Mock()
        mock_image.open.return_value = mock_pil_image
        
        # Executar teste
        client = GeminiImagenClient(api_key=self.api_key)
        result = client.generate_image(self.test_prompt)
        
        # Verificar resultado
        assert result['image'] == mock_pil_image
        assert result['text_response'] == "Imagem gerada com sucesso"
        assert result['saved_path'] is None
        
        # Verificar que a API foi chamada corretamente
        mock_client_instance.models.generate_content.assert_called_once()
    
    @patch('gemini_imagen_client.genai.Client')
    @patch('gemini_imagen_client.Image')
    @patch('gemini_imagen_client.Path')
    def test_generate_image_with_save(self, mock_path, mock_image, mock_client):
        """Testa geração de imagem com salvamento."""
        # Configurar mocks
        mock_response = Mock()
        mock_part = Mock()
        mock_part.text = None
        mock_part.inline_data = Mock()
        mock_part.inline_data.data = b"fake_image_data"
        mock_response.candidates = [Mock()]
        mock_response.candidates[0].content.parts = [mock_part]
        
        mock_client_instance = Mock()
        mock_client_instance.models.generate_content.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        mock_pil_image = Mock()
        mock_image.open.return_value = mock_pil_image
        
        mock_path_instance = Mock()
        mock_path_instance.parent.mkdir = Mock()
        mock_path.return_value = mock_path_instance
        
        # Executar teste
        client = GeminiImagenClient(api_key=self.api_key)
        output_path = "test_output.png"
        result = client.generate_image(self.test_prompt, output_path=output_path)
        
        # Verificar resultado
        assert result['image'] == mock_pil_image
        assert result['saved_path'] == str(mock_path_instance)
        
        # Verificar que a imagem foi salva
        mock_pil_image.save.assert_called_once_with(mock_path_instance)
    
    @patch('gemini_imagen_client.genai.Client')
    def test_generate_image_no_image_in_response(self, mock_client):
        """Testa erro quando não há imagem na resposta."""
        # Configurar mock para resposta sem imagem
        mock_response = Mock()
        mock_part = Mock()
        mock_part.text = "Apenas texto"
        mock_part.inline_data = None
        mock_response.candidates = [Mock()]
        mock_response.candidates[0].content.parts = [mock_part]
        
        mock_client_instance = Mock()
        mock_client_instance.models.generate_content.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        # Executar teste e verificar erro
        client = GeminiImagenClient(api_key=self.api_key)
        with pytest.raises(Exception, match="Nenhuma imagem foi gerada"):
            client.generate_image(self.test_prompt)
    
    @patch('gemini_imagen_client.genai.Client')
    def test_generate_image_api_error(self, mock_client):
        """Testa tratamento de erro da API."""
        # Configurar mock para erro da API
        mock_client_instance = Mock()
        mock_client_instance.models.generate_content.side_effect = Exception("API Error")
        mock_client.return_value = mock_client_instance
        
        # Executar teste e verificar erro
        client = GeminiImagenClient(api_key=self.api_key)
        with pytest.raises(Exception, match="Erro ao gerar imagem: API Error"):
            client.generate_image(self.test_prompt)
    
    def test_generate_multiple_images(self):
        """Testa geração de múltiplas imagens."""
        with patch.object(GeminiImagenClient, 'generate_image') as mock_generate:
            # Configurar mock para retornar sucesso
            mock_generate.return_value = {
                'image': Mock(),
                'text_response': 'Sucesso',
                'saved_path': 'test.png'
            }
            
            client = GeminiImagenClient(api_key=self.api_key)
            prompts = ["prompt1", "prompt2"]
            results = client.generate_multiple_images(prompts)
            
            # Verificar que foi chamado para cada prompt
            assert len(results) == 2
            assert mock_generate.call_count == 2
            
            # Verificar estrutura dos resultados
            for i, result in enumerate(results):
                assert result['prompt'] == prompts[i]
                assert result['index'] == i
    
    @pytest.mark.asyncio
    async def test_generate_image_async(self):
        """Testa geração assíncrona de imagem."""
        with patch.object(GeminiImagenClient, 'generate_image') as mock_generate:
            mock_generate.return_value = {
                'image': Mock(),
                'text_response': 'Sucesso async',
                'saved_path': None
            }
            
            client = GeminiImagenClient(api_key=self.api_key)
            result = await client.generate_image_async(self.test_prompt)
            
            assert result['text_response'] == 'Sucesso async'
            mock_generate.assert_called_once_with(
                self.test_prompt, None, True
            )
    
    @pytest.mark.asyncio
    async def test_generate_multiple_images_async(self):
        """Testa geração assíncrona de múltiplas imagens."""
        with patch.object(GeminiImagenClient, 'generate_image_async') as mock_generate_async:
            mock_generate_async.return_value = {
                'image': Mock(),
                'text_response': 'Sucesso',
                'saved_path': 'test.png'
            }
            
            client = GeminiImagenClient(api_key=self.api_key)
            prompts = ["prompt1", "prompt2"]
            results = await client.generate_multiple_images_async(prompts)
            
            assert len(results) == 2
            assert mock_generate_async.call_count == 2
    
    @patch('gemini_imagen_client.genai.Client')
    @patch('gemini_imagen_client.Image')
    @patch('gemini_imagen_client.Path')
    def test_edit_image_success(self, mock_path, mock_image, mock_client):
        """Testa edição bem-sucedida de imagem."""
        # Configurar mocks
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        mock_original_image = Mock()
        mock_edited_image = Mock()
        mock_image.open.side_effect = [mock_original_image, mock_edited_image]
        
        mock_response = Mock()
        mock_part = Mock()
        mock_part.text = "Imagem editada"
        mock_part.inline_data = Mock()
        mock_part.inline_data.data = b"edited_image_data"
        mock_response.candidates = [Mock()]
        mock_response.candidates[0].content.parts = [mock_part]
        
        mock_client_instance = Mock()
        mock_client_instance.models.generate_content.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        # Executar teste
        client = GeminiImagenClient(api_key=self.api_key)
        result = client.edit_image(
            image_path="original.png",
            edit_prompt="Adicione um chapéu",
            output_path="edited.png"
        )
        
        # Verificar resultado
        assert result['image'] == mock_edited_image
        assert result['text_response'] == "Imagem editada"
        assert 'original_image_path' in result
    
    @patch('gemini_imagen_client.Path')
    def test_edit_image_file_not_found(self, mock_path):
        """Testa erro quando arquivo de imagem não existe."""
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance
        
        client = GeminiImagenClient(api_key=self.api_key)
        with pytest.raises(Exception, match="Erro ao editar imagem"):
            client.edit_image(
                image_path="nonexistent.png",
                edit_prompt="Editar"
            )
    
    def test_get_model_info(self):
        """Testa obtenção de informações do modelo."""
        client = GeminiImagenClient(api_key=self.api_key)
        info = client.get_model_info()
        
        assert info['model_name'] == "gemini-2.0-flash-exp"
        assert info['api_type'] == 'Google Gemini API'
        assert 'capabilities' in info
        assert 'response_modalities' in info


class TestConvenienceFunctions:
    """Testes para funções de conveniência."""
    
    @patch('gemini_imagen_client.GeminiImagenClient')
    def test_generate_image_quick(self, mock_client_class):
        """Testa função de conveniência generate_image_quick."""
        # Configurar mock
        mock_client = Mock()
        mock_client.generate_image.return_value = {'saved_path': 'quick_test.png'}
        mock_client_class.return_value = mock_client
        
        # Executar teste
        result = generate_image_quick(
            prompt="Teste rápido",
            output_path="quick_test.png",
            api_key="test_key"
        )
        
        # Verificar resultado
        assert result == 'quick_test.png'
        mock_client_class.assert_called_once_with(api_key="test_key")
        mock_client.generate_image.assert_called_once_with(
            prompt="Teste rápido",
            output_path="quick_test.png"
        )


class TestIntegration:
    """Testes de integração (requerem API key real)."""
    
    @pytest.mark.skipif(
        not os.getenv('GEMINI_API_KEY'),
        reason="Requer GEMINI_API_KEY para teste de integração"
    )
    def test_real_api_integration(self):
        """Teste de integração com API real (apenas se API key disponível)."""
        client = GeminiImagenClient()
        
        # Teste básico de geração
        try:
            result = client.generate_image(
                prompt="Um simples círculo azul",
                include_text_response=False
            )
            
            # Verificar que uma imagem foi gerada
            assert result['image'] is not None
            assert hasattr(result['image'], 'save')  # Verificar que é um objeto PIL
            
        except Exception as e:
            pytest.fail(f"Teste de integração falhou: {e}")


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v"])