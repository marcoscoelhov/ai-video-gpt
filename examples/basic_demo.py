#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Unificado - AI Video GPT

Este arquivo consolida todas as demonstrações do sistema em um único local.

Uso:
    python demo.py --type [video|gemini|imagen|subtitles|tiktok]
    python demo.py --interactive  # Modo interativo
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Carrega variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv não instalado. Instale com: pip install python-dotenv")

# Adiciona o diretório raiz ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class DemoSystem:
    def __init__(self):
        self.output_dir = Path("outputs/demos")
        self.output_dir.mkdir(exist_ok=True)
        
        # Configurações de demo
        self.demo_configs = {
            'video_basico': {
                'prompt': 'Um gato astronauta explorando uma estação espacial futurística',
                'duration': 10,
                'format': '16:9',
                'description': 'Demonstração básica de geração de vídeo'
            },
            'tiktok': {
                'prompt': 'Robô dançando em uma cidade cyberpunk com luzes neon',
                'duration': 15,
                'format': '9:16',
                'description': 'Demonstração do formato TikTok (9:16)'
            },
            'fantasia': {
                'prompt': 'Dragão voando sobre um castelo mágico ao pôr do sol',
                'duration': 12,
                'format': '16:9',
                'description': 'Demonstração com tema fantasia'
            }
        }
    
    def print_header(self, title):
        """Imprime cabeçalho formatado"""
        print("\n" + "=" * 60)
        print(f"🎬 {title}")
        print("=" * 60)
    
    def demo_video_generation(self):
        """Demonstração de geração de vídeo completo"""
        self.print_header("DEMO: Geração de Vídeo Completo")
        
        try:
            from main import main as generate_video
            
            config = self.demo_configs['video_basico']
            
            print(f"📝 Prompt: {config['prompt']}")
            print(f"⏱️  Duração: {config['duration']} segundos")
            print(f"📐 Formato: {config['format']}")
            print("\n🚀 Iniciando geração...")
            
            # A função main só aceita theme como parâmetro
            result = generate_video(config['prompt'])
            
            if result:
                print("✅ Vídeo gerado com sucesso!")
                output_file = self.output_dir / "final_video.mp4"
                if output_file.exists():
                    size_mb = output_file.stat().st_size / 1024 / 1024
                    print(f"📁 Arquivo: {output_file}")
                    print(f"📊 Tamanho: {size_mb:.2f} MB")
                return True
            else:
                print("❌ Falha na geração do vídeo")
                return False
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def demo_tiktok_format(self):
        """Demonstração específica do formato TikTok"""
        self.print_header("DEMO: Formato TikTok (9:16)")
        
        try:
            from generate_tiktok_video import main as generate_tiktok
            
            config = self.demo_configs['tiktok']
            
            print(f"📱 Formato TikTok otimizado (720x1280)")
            print(f"📝 Prompt: {config['prompt']}")
            print(f"⏱️  Duração: {config['duration']} segundos")
            print("\n🚀 Iniciando geração...")
            
            # Chama a função de geração TikTok
            result = generate_tiktok(
                prompt=config['prompt'],
                duration=config['duration'],
                output_dir=str(self.output_dir)
            )
            
            if result:
                print("✅ Vídeo TikTok gerado com sucesso!")
                print(f"📱 Resolução: 720x1280 (9:16)")
                return True
            else:
                print("❌ Falha na geração do vídeo TikTok")
                return False
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def demo_gemini_imagen(self):
        """Demonstração do Gemini Imagen"""
        self.print_header("DEMO: Gemini Imagen")
        
        try:
            from config.gemini_imagen_client import GeminiImagenClient
            from core.subtitle_styles import SubtitleStyleManager, SubtitleStyle
            
            print("🤖 Testando integração com Gemini Imagen...")
            
            client = GeminiImagenClient()
            
            # Teste simples de geração de imagem
            prompt = "Um robô fofo em estilo cartoon explorando uma cidade futurística"
            print(f"📝 Prompt de teste: {prompt}")
            
            print("\n🎨 Gerando imagem real...")
            
            # Gera imagem real
            output_path = self.output_dir / "demo_gemini_imagen.png"
            
            # Gera imagem usando o método correto
            result = client.generate_image(
                prompt=prompt,
                output_path=str(output_path)
            )
            
            if result:
                print("✅ Imagem gerada com sucesso!")
                print(f"📁 Salva em: {output_path}")
                print(f"📊 Tamanho: {output_path.stat().st_size / 1024:.2f} KB")
                return True
            else:
                print("❌ Falha na geração da imagem")
                return False
            
        except Exception as e:
            print(f"❌ Erro na geração do Gemini Imagen: {e}")
            return False
    
    def demo_subtitle_system(self):
        """Demonstração do sistema de legendas"""
        self.print_header("DEMO: Sistema de Legendas")
        
        try:
            from config.gemini_subtitle_client import GeminiSubtitleClient
            
            print("🎵 Testando sistema de legendas com Gemini...")
            
            client = GeminiSubtitleClient()
            
            # Verifica se existe arquivo de áudio de exemplo
            audio_files = list(Path("outputs/videos").glob("**/*.mp3"))
            
            if audio_files:
                audio_file = audio_files[0]
                print(f"🎧 Arquivo de áudio encontrado: {audio_file.name}")
                print(f"📊 Tamanho: {audio_file.stat().st_size / 1024:.2f} KB")
            else:
                print("📝 Nenhum arquivo de áudio encontrado para demonstração")
            
            # Demonstra formato JSON de legendas
            sample_subtitles = {
                "subtitles": [
                    {
                        "start_time": 0.0,
                        "end_time": 2.5,
                        "text": "Bem-vindos ao futuro da criação de vídeos"
                    },
                    {
                        "start_time": 2.5,
                        "end_time": 5.0,
                        "text": "Onde a inteligência artificial encontra a criatividade"
                    }
                ]
            }
            
            subtitle_file = self.output_dir / "demo_subtitles.json"
            with open(subtitle_file, 'w', encoding='utf-8') as f:
                json.dump(sample_subtitles, f, indent=2, ensure_ascii=False)
            
            print("✅ Sistema de legendas inicializado com sucesso!")
            print(f"📁 Exemplo de legendas salvo em: {subtitle_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no sistema de legendas: {e}")
            return False
    
    def demo_subtitle_styles(self):
        """Demonstração dos diferentes estilos de legendas"""
        self.print_header("DEMO: Estilos de Legendas")
        
        try:
            from core.subtitle_styles import get_available_styles, SubtitleStyleManager
            
            # Mostrar estilos disponíveis
            available_styles = SubtitleStyleManager.STYLES
            print(f"🎨 Estilos disponíveis: {', '.join(available_styles.keys())}")
            
            # Demonstrar cada estilo
            for style_name in available_styles:
                style = SubtitleStyleManager.get_style(style_name)
                print(f"\n--- Estilo: {style_name.upper()} ---")
                
                descriptions = {
                    "netflix": "Estilo Netflix - Fonte bold, alta legibilidade",
                    "youtube": "Estilo YouTube - Moderno e limpo",
                    "cinema": "Estilo Cinema - Elegante com sombra",
                    "modern": "Estilo Moderno - Equilibrado e profissional",
                    "accessibility": "Estilo Acessibilidade - Alto contraste para deficientes visuais",
                    "pop": "Estilo Pop - Vibrante e moderno para redes sociais"
                }
                print(f"📖 Descrição: {descriptions.get(style_name, 'N/A')}")

                print(f"📝 Fonte: {style.font_family}, Tamanho: {style.font_size}")
                print(f"🎨 Cor: {style.text_color}, Fundo: {style.background_color}")
                print(f"📍 Posição: {style.position_v} {style.position_h}")
                print(f"🔲 Contorno: {style.outline_width}px {style.outline_color}")
                
                # Exemplo de filtro FFmpeg
                sample_srt = "sample.srt"
                filter_example = SubtitleStyleManager.generate_ffmpeg_subtitle_filter(style, sample_srt)
                print(f"⚙️ Filtro FFmpeg: {filter_example}")
            
            # Criar estilo personalizado
            custom_style = SubtitleStyleManager.create_custom_style(
                font_size=28,
                text_color="#FFD700",  # Dourado
                background_color="#000080",  # Azul escuro
                position_v="bottom",
                position_h="center"
            )
            print(f"\n--- Estilo Personalizado ---")
            print(f"📝 Fonte: {custom_style.font_family}, Tamanho: {custom_style.font_size}")
            print(f"🎨 Cor: {custom_style.text_color}, Fundo: {custom_style.background_color}")
            print(f"📍 Posição: {custom_style.position_v} {custom_style.position_h}")
            
            print("✅ Demonstração de estilos concluída com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro na demonstração de estilos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def demo_interactive(self):
        """Modo interativo para escolher demos"""
        self.print_header("MODO INTERATIVO")
        
        demos = {
            '1': ('Geração de Vídeo Completo', self.demo_video_generation),
            '2': ('Formato TikTok (9:16)', self.demo_tiktok_format),
            '3': ('Gemini Imagen', self.demo_gemini_imagen),
            '4': ('Sistema de Legendas', self.demo_subtitle_system),
            '5': ('Estilos de Legendas', self.demo_subtitle_styles),
            '6': ('Todos os Demos', self.run_all_demos)
        }
        
        print("Escolha uma demonstração:")
        for key, (name, _) in demos.items():
            print(f"  {key}. {name}")
        
        while True:
            choice = input("\n👉 Digite sua escolha (1-6) ou 'q' para sair: ").strip()
            
            if choice.lower() == 'q':
                print("👋 Até logo!")
                break
            
            if choice in demos:
                name, func = demos[choice]
                print(f"\n🎯 Executando: {name}")
                func()
                
                continue_demo = input("\n❓ Deseja executar outro demo? (s/n): ").strip().lower()
                if continue_demo != 's':
                    break
            else:
                print("❌ Escolha inválida. Tente novamente.")
    
    def run_all_demos(self):
        """Executa todas as demonstrações"""
        self.print_header("EXECUTANDO TODOS OS DEMOS")
        
        demos = [
            ("Gemini Imagen", self.demo_gemini_imagen),
            ("Sistema de Legendas", self.demo_subtitle_system),
            ("Estilos de Legendas", self.demo_subtitle_styles),
            ("Formato TikTok", self.demo_tiktok_format),
            ("Geração de Vídeo", self.demo_video_generation)
        ]
        
        results = []
        
        for name, demo_func in demos:
            print(f"\n🎯 Executando demo: {name}")
            try:
                result = demo_func()
                results.append((name, result))
            except Exception as e:
                print(f"❌ Erro no demo {name}: {e}")
                results.append((name, False))
        
        # Resumo final
        self.print_header("RESUMO DOS DEMOS")
        
        for name, result in results:
            status = "✅ SUCESSO" if result else "❌ FALHA"
            print(f"{status} - {name}")
        
        successful = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"\n📊 Resultado: {successful}/{total} demos executados com sucesso")
        
        return successful == total

def main():
    parser = argparse.ArgumentParser(description='Sistema de Demo Unificado')
    parser.add_argument('--type', choices=['video', 'gemini', 'imagen', 'subtitles', 'styles', 'tiktok', 'all'], 
                       default='all', help='Tipo de demonstração')
    parser.add_argument('--interactive', action='store_true', 
                       help='Modo interativo')
    
    args = parser.parse_args()
    
    demo_system = DemoSystem()
    
    if args.interactive:
        demo_system.demo_interactive()
    elif args.type == 'all':
        demo_system.run_all_demos()
    elif args.type == 'video':
        demo_system.demo_video_generation()
    elif args.type == 'tiktok':
        demo_system.demo_tiktok_format()
    elif args.type == 'gemini' or args.type == 'imagen':
        demo_system.demo_gemini_imagen()
    elif args.type == 'subtitles':
        demo_system.demo_subtitle_system()
    elif args.type == 'styles':
        demo_system.demo_subtitle_styles()

if __name__ == "__main__":
    main()