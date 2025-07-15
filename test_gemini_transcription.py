"""Teste das capacidades de transcrição do Gemini 2.0 Flash."""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Carregar variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv não encontrado. Certifique-se de que as variáveis de ambiente estão configuradas.")

from gemini_imagen_client import GeminiImagenClient
import google.generativeai as genai

def test_gemini_audio_transcription():
    """Testa a capacidade de transcrição de áudio do Gemini."""
    
    # Configurar API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY não encontrada no arquivo .env")
        return False
    
    try:
        # Configurar Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        print("🎵 Testando transcrição de áudio com Gemini 2.0 Flash...")
        
        # Verificar se existe algum arquivo de áudio para testar
        audio_dirs = [
            "output/video_um_robô_explorando_uma_cidade_futurística_20250715_201003/audio",
            "outputs"
        ]
        
        audio_file = None
        for audio_dir in audio_dirs:
            if os.path.exists(audio_dir):
                for file in os.listdir(audio_dir):
                    if file.endswith(('.mp3', '.wav', '.m4a')):
                        audio_file = os.path.join(audio_dir, file)
                        break
                if audio_file:
                    break
        
        if not audio_file:
            print("❌ Nenhum arquivo de áudio encontrado para teste")
            return False
        
        print(f"📁 Usando arquivo: {audio_file}")
        
        # Upload do arquivo de áudio
        audio_upload = genai.upload_file(audio_file)
        print(f"✅ Arquivo enviado: {audio_upload.name}")
        
        # Prompt para transcrição com timestamps
        prompt = """
        Transcreva este áudio em português brasileiro.
        
        Formato de saída desejado (SRT):
        número_da_legenda
        timestamp_inicio --> timestamp_fim
        texto_da_fala
        
        Exemplo:
        1
        00:00:00,000 --> 00:00:03,500
        Olá, este é um teste.
        
        2
        00:00:03,500 --> 00:00:07,000
        Esta é a segunda frase.
        
        Por favor, seja preciso com os timestamps e mantenha as legendas curtas (máximo 2 linhas).
        """
        
        # Gerar transcrição
        response = model.generate_content([prompt, audio_upload])
        
        print("\n📝 Transcrição gerada:")
        print("=" * 50)
        print(response.text)
        print("=" * 50)
        
        # Salvar resultado
        output_file = "test_transcription_output.srt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print(f"\n💾 Transcrição salva em: {output_file}")
        
        # Limpar arquivo temporário
        genai.delete_file(audio_upload.name)
        print("🗑️ Arquivo temporário removido")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Teste de Transcrição com Gemini 2.0 Flash")
    print("=" * 50)
    
    success = test_gemini_audio_transcription()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Verificar a qualidade da transcrição")
        print("2. Avaliar a precisão dos timestamps")
        print("3. Implementar a classe GeminiSubtitleClient")
    else:
        print("\n❌ Teste falhou. Verifique os logs acima.")