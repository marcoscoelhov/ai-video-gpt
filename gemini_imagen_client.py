"""Cliente simplificado para geração de imagens com Google Gemini 2.0 Flash.

Este módulo fornece uma interface simplificada para gerar imagens usando o
Google Gemini 2.0 Flash, encapsulando a complexidade da API e oferecendo
métodos síncronos e assíncronos para geração de imagens.

Exemplo de uso:
    from gemini_imagen_client import GeminiImagenClient
    
    # Inicializar o cliente
    client = GeminiImagenClient(api_key="sua_api_key")
    
    # Gerar uma imagem
    image_path = client.generate_image(
        prompt="Um gato astronauta dirigindo um buggy lunar",
        output_path="imagem_gerada.png"
    )
    
    print(f"Imagem salva em: {image_path}")
"""

import os
import asyncio
from io import BytesIO
from typing import Optional, Union, List, Dict, Any
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise ImportError(
        "PIL (Pillow) é necessário para salvar imagens. "
        "Instale com: pip install Pillow"
    )

try:
    from google import genai
    from google.genai import types
except ImportError:
    raise ImportError(
        "google-genai é necessário para usar o Gemini API. "
        "Instale com: pip install google-genai"
    )


class GeminiImagenClient:
    """Cliente simplificado para geração de imagens com Google Gemini 2.0 Flash.
    
    Esta classe encapsula a complexidade da API do Google Gemini 2.0 Flash,
    fornecendo uma interface simples para gerar imagens a partir de prompts de texto.
    
    Attributes:
        model_name (str): Nome do modelo Gemini usado para geração de imagens.
        client: Cliente da API Gemini configurado.
        config: Configuração para geração de conteúdo multimodal.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.0-flash-exp"):
        """Inicializa o cliente Gemini para geração de imagens.
        
        Args:
            api_key (Optional[str]): Chave da API do Google Gemini.
                                   Se não fornecida, tentará obter da variável
                                   de ambiente GEMINI_API_KEY.
            model_name (str): Nome do modelo Gemini a ser usado.
                            Padrão: "gemini-2.0-flash-exp"
        
        Raises:
            ValueError: Se a API key não for fornecida nem encontrada nas
                       variáveis de ambiente.
        """
        # Obter API key
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key is None:
                raise ValueError(
                    "API key não fornecida. Forneça via parâmetro api_key ou "
                    "defina a variável de ambiente GEMINI_API_KEY."
                )
        
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)
        
        # Configuração para geração de imagens
        self.config = types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
        )
    
    def generate_image(
        self,
        prompt: str,
        output_path: Optional[Union[str, Path]] = None,
        include_text_response: bool = True
    ) -> Dict[str, Any]:
        """Gera uma imagem a partir de um prompt de texto.
        
        Args:
            prompt (str): Descrição da imagem a ser gerada.
            output_path (Optional[Union[str, Path]]): Caminho onde salvar a imagem.
                                                    Se não fornecido, a imagem não será salva.
            include_text_response (bool): Se deve incluir resposta de texto junto com a imagem.
        
        Returns:
            Dict[str, Any]: Dicionário contendo:
                - 'image': Objeto PIL Image da imagem gerada
                - 'text_response': Texto gerado (se include_text_response=True)
                - 'saved_path': Caminho onde a imagem foi salva (se output_path fornecido)
        
        Raises:
            Exception: Se houver erro na geração da imagem.
        """
        try:
            # Fazer a requisição para o Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.config
            )
            
            result = {
                'image': None,
                'text_response': None,
                'saved_path': None
            }
            
            # Processar a resposta
            for part in response.candidates[0].content.parts:
                if part.text is not None and include_text_response:
                    result['text_response'] = part.text
                elif part.inline_data is not None:
                    # Converter dados da imagem para PIL Image
                    image = Image.open(BytesIO(part.inline_data.data))
                    result['image'] = image
                    
                    # Salvar imagem se caminho fornecido
                    if output_path:
                        output_path = Path(output_path)
                        # Criar diretório se não existir
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Salvar imagem
                        image.save(output_path)
                        result['saved_path'] = str(output_path)
            
            if result['image'] is None:
                raise Exception("Nenhuma imagem foi gerada na resposta.")
            
            return result
            
        except Exception as e:
            raise Exception(f"Erro ao gerar imagem: {str(e)}")
    
    async def generate_image_async(
        self,
        prompt: str,
        output_path: Optional[Union[str, Path]] = None,
        include_text_response: bool = True
    ) -> Dict[str, Any]:
        """Versão assíncrona da geração de imagem.
        
        Args:
            prompt (str): Descrição da imagem a ser gerada.
            output_path (Optional[Union[str, Path]]): Caminho onde salvar a imagem.
            include_text_response (bool): Se deve incluir resposta de texto.
        
        Returns:
            Dict[str, Any]: Mesmo formato do método síncrono.
        """
        # Executar em thread separada para não bloquear o loop de eventos
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.generate_image,
            prompt,
            output_path,
            include_text_response
        )
    
    def generate_multiple_images(
        self,
        prompts: List[str],
        output_dir: Optional[Union[str, Path]] = None,
        filename_prefix: str = "gemini_image",
        include_text_responses: bool = True
    ) -> List[Dict[str, Any]]:
        """Gera múltiplas imagens a partir de uma lista de prompts.
        
        Args:
            prompts (List[str]): Lista de prompts para gerar imagens.
            output_dir (Optional[Union[str, Path]]): Diretório onde salvar as imagens.
            filename_prefix (str): Prefixo para os nomes dos arquivos.
            include_text_responses (bool): Se deve incluir respostas de texto.
        
        Returns:
            List[Dict[str, Any]]: Lista de resultados, um para cada prompt.
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            output_path = None
            if output_dir:
                output_dir = Path(output_dir)
                output_path = output_dir / f"{filename_prefix}_{i+1:03d}.png"
            
            try:
                result = self.generate_image(
                    prompt=prompt,
                    output_path=output_path,
                    include_text_response=include_text_responses
                )
                result['prompt'] = prompt
                result['index'] = i
                results.append(result)
            except Exception as e:
                # Adicionar erro ao resultado
                results.append({
                    'prompt': prompt,
                    'index': i,
                    'error': str(e),
                    'image': None,
                    'text_response': None,
                    'saved_path': None
                })
        
        return results
    
    async def generate_multiple_images_async(
        self,
        prompts: List[str],
        output_dir: Optional[Union[str, Path]] = None,
        filename_prefix: str = "gemini_image",
        include_text_responses: bool = True,
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """Versão assíncrona para gerar múltiplas imagens.
        
        Args:
            prompts (List[str]): Lista de prompts para gerar imagens.
            output_dir (Optional[Union[str, Path]]): Diretório onde salvar as imagens.
            filename_prefix (str): Prefixo para os nomes dos arquivos.
            include_text_responses (bool): Se deve incluir respostas de texto.
            max_concurrent (int): Número máximo de requisições simultâneas.
        
        Returns:
            List[Dict[str, Any]]: Lista de resultados, um para cada prompt.
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_single(i: int, prompt: str) -> Dict[str, Any]:
            async with semaphore:
                output_path = None
                if output_dir:
                    output_dir_path = Path(output_dir)
                    output_path = output_dir_path / f"{filename_prefix}_{i+1:03d}.png"
                
                try:
                    result = await self.generate_image_async(
                        prompt=prompt,
                        output_path=output_path,
                        include_text_response=include_text_responses
                    )
                    result['prompt'] = prompt
                    result['index'] = i
                    return result
                except Exception as e:
                    return {
                        'prompt': prompt,
                        'index': i,
                        'error': str(e),
                        'image': None,
                        'text_response': None,
                        'saved_path': None
                    }
        
        # Executar todas as tarefas concorrentemente
        tasks = [generate_single(i, prompt) for i, prompt in enumerate(prompts)]
        results = await asyncio.gather(*tasks)
        
        return results
    
    def edit_image(
        self,
        image_path: Union[str, Path],
        edit_prompt: str,
        output_path: Optional[Union[str, Path]] = None,
        include_text_response: bool = True
    ) -> Dict[str, Any]:
        """Edita uma imagem existente usando um prompt de texto.
        
        Args:
            image_path (Union[str, Path]): Caminho para a imagem a ser editada.
            edit_prompt (str): Descrição das edições a serem feitas.
            output_path (Optional[Union[str, Path]]): Caminho onde salvar a imagem editada.
            include_text_response (bool): Se deve incluir resposta de texto.
        
        Returns:
            Dict[str, Any]: Resultado da edição no mesmo formato de generate_image.
        
        Raises:
            FileNotFoundError: Se a imagem não for encontrada.
            Exception: Se houver erro na edição da imagem.
        """
        try:
            # Carregar a imagem
            if not Path(image_path).exists():
                raise FileNotFoundError(f"Imagem não encontrada: {image_path}")
            
            image = Image.open(image_path)
            
            # Fazer a requisição para o Gemini com imagem e prompt
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[edit_prompt, image],
                config=self.config
            )
            
            result = {
                'image': None,
                'text_response': None,
                'saved_path': None,
                'original_image_path': str(image_path)
            }
            
            # Processar a resposta
            for part in response.candidates[0].content.parts:
                if part.text is not None and include_text_response:
                    result['text_response'] = part.text
                elif part.inline_data is not None:
                    # Converter dados da imagem para PIL Image
                    edited_image = Image.open(BytesIO(part.inline_data.data))
                    result['image'] = edited_image
                    
                    # Salvar imagem se caminho fornecido
                    if output_path:
                        output_path = Path(output_path)
                        # Criar diretório se não existir
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Salvar imagem
                        edited_image.save(output_path)
                        result['saved_path'] = str(output_path)
            
            if result['image'] is None:
                raise Exception("Nenhuma imagem editada foi gerada na resposta.")
            
            return result
            
        except Exception as e:
            raise Exception(f"Erro ao editar imagem: {str(e)}")
    
    def get_model_info(self) -> Dict[str, str]:
        """Retorna informações sobre o modelo sendo usado.
        
        Returns:
            Dict[str, str]: Informações do modelo.
        """
        return {
            'model_name': self.model_name,
            'api_type': 'Google Gemini API',
            'capabilities': 'Text-to-Image, Image-to-Image, Multimodal Generation',
            'response_modalities': str(self.config.response_modalities)
        }


# Função de conveniência para uso rápido
def generate_image_quick(
    prompt: str,
    output_path: str,
    api_key: Optional[str] = None
) -> str:
    """Função de conveniência para gerar uma imagem rapidamente.
    
    Args:
        prompt (str): Descrição da imagem a ser gerada.
        output_path (str): Caminho onde salvar a imagem.
        api_key (Optional[str]): Chave da API (opcional).
    
    Returns:
        str: Caminho onde a imagem foi salva.
    
    Raises:
        Exception: Se houver erro na geração.
    """
    client = GeminiImagenClient(api_key=api_key)
    result = client.generate_image(prompt=prompt, output_path=output_path)
    return result['saved_path']


if __name__ == "__main__":
    # Exemplo de uso
    import sys
    
    # Verificar se API key está disponível
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Erro: Defina a variável de ambiente GEMINI_API_KEY")
        sys.exit(1)
    
    # Criar cliente
    client = GeminiImagenClient()
    
    # Exemplo de geração de imagem
    try:
        print("Gerando imagem...")
        result = client.generate_image(
            prompt="Um gato astronauta dirigindo um buggy lunar com a Terra ao fundo",
            output_path="exemplo_gemini.png"
        )
        
        print(f"Imagem salva em: {result['saved_path']}")
        if result['text_response']:
            print(f"Resposta de texto: {result['text_response']}")
        
        # Mostrar informações do modelo
        info = client.get_model_info()
        print(f"\nInformações do modelo: {info}")
        
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)