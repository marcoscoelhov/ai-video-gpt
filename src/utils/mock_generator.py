#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock Generator - Simulador de APIs sem Custos

Este módulo simula as respostas das APIs (Gemini, ElevenLabs) para testes
sem gerar custos reais, permitindo validação de funcionalidades.

Autor: AI Video GPT
Data: 2025-01-19
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class MockGenerator:
    """Gerador de dados mock para simular APIs."""
    
    def __init__(self):
        self.mock_data_dir = Path("mock_data")
        self.mock_data_dir.mkdir(exist_ok=True)
        
        # Templates para geração de conteúdo mock
        self.visual_templates = [
            "Close-up shot with dramatic lighting and vibrant colors",
            "Wide establishing shot with cinematic composition",
            "Dynamic action scene with motion blur effects",
            "Atmospheric scene with moody lighting and shadows",
            "Detailed macro shot with shallow depth of field",
            "Aerial view with sweeping camera movement",
            "Intimate portrait with soft, natural lighting",
            "Epic landscape with golden hour illumination"
        ]
        
        self.narration_templates = [
            "Uma jornada épica começa aqui.",
            "O mistério se aprofunda a cada momento.",
            "A aventura continua sem parar.",
            "Descobertas surpreendentes aguardam.",
            "O destino final se aproxima.",
            "Cada passo revela novos segredos.",
            "A história ganha vida diante dos olhos.",
            "O clímax da narrativa se desenrola."
        ]
        
        self.themes = {
            'space': ['astronauta', 'galáxia', 'planeta', 'nave espacial', 'estrelas'],
            'fantasy': ['dragão', 'castelo', 'magia', 'floresta encantada', 'cristal'],
            'cyberpunk': ['robô', 'neon', 'cidade futurística', 'hacker', 'inteligência artificial'],
            'nature': ['floresta', 'oceano', 'montanha', 'animal selvagem', 'pôr do sol'],
            'adventure': ['explorador', 'tesouro', 'mapa', 'jornada', 'descoberta']
        }
    
    def mock_script_generation(self, prompt: str, scenes: int = 3) -> Dict:
        """Simula geração de script pelo Gemini."""
        # Detectar tema baseado no prompt
        theme_detected = 'adventure'  # padrão
        for theme, keywords in self.themes.items():
            if any(keyword in prompt.lower() for keyword in keywords):
                theme_detected = theme
                break
        
        # Gerar título baseado no prompt
        title_words = prompt.split()[:3]  # Primeiras 3 palavras
        title = ' '.join(word.capitalize() for word in title_words)
        
        mock_script = {
            "theme": prompt,
            "title": title,
            "scenes": [],
            "_mock_info": {
                "generated_at": datetime.now().isoformat(),
                "theme_detected": theme_detected,
                "cost_saved": 0.01  # Custo estimado de geração real
            }
        }
        
        # Gerar cenas
        for i in range(scenes):
            # Selecionar elementos temáticos
            theme_keywords = self.themes[theme_detected]
            selected_keyword = random.choice(theme_keywords)
            
            scene = {
                "scene": i + 1,
                "visual_description": f"{selected_keyword} - {random.choice(self.visual_templates)}",
                "narration": random.choice(self.narration_templates)
            }
            mock_script["scenes"].append(scene)
        
        return mock_script
    
    def mock_image_generation(self, descriptions: List[str]) -> List[str]:
        """Simula geração de imagens pelo Gemini Imagen."""
        mock_images = []
        
        for i, description in enumerate(descriptions):
            # Criar arquivo mock de imagem (texto simulando PNG)
            mock_image_path = self.mock_data_dir / f"mock_image_{i+1:03d}.png"
            
            # Simular metadados da imagem
            mock_metadata = {
                "description": description,
                "generated_at": datetime.now().isoformat(),
                "dimensions": "1024x1024",
                "format": "PNG",
                "cost_saved": 0.04,  # Custo estimado por imagem
                "_mock": True
            }
            
            # Salvar metadados como arquivo de texto (simulando imagem)
            with open(mock_image_path, 'w', encoding='utf-8') as f:
                f.write(f"MOCK IMAGE FILE\n")
                f.write(f"Description: {description}\n")
                f.write(f"Generated: {datetime.now()}\n")
                f.write(json.dumps(mock_metadata, indent=2))
            
            mock_images.append(str(mock_image_path))
        
        return mock_images
    
    def mock_audio_generation(self, texts: List[str], voice: str = "pt-BR") -> List[str]:
        """Simula geração de áudio pelo gTTS ou ElevenLabs."""
        mock_audios = []
        
        for i, text in enumerate(texts):
            # Criar arquivo mock de áudio
            mock_audio_path = self.mock_data_dir / f"mock_audio_{i+1:03d}.mp3"
            
            # Simular duração baseada no texto
            estimated_duration = len(text.split()) * 0.5  # ~0.5s por palavra
            
            mock_metadata = {
                "text": text,
                "voice": voice,
                "duration_seconds": estimated_duration,
                "generated_at": datetime.now().isoformat(),
                "format": "MP3",
                "bitrate": "128kbps",
                "cost_saved": 0.02,  # Custo estimado por áudio
                "_mock": True
            }
            
            # Salvar metadados como arquivo de texto (simulando áudio)
            with open(mock_audio_path, 'w', encoding='utf-8') as f:
                f.write(f"MOCK AUDIO FILE\n")
                f.write(f"Text: {text}\n")
                f.write(f"Duration: {estimated_duration:.1f}s\n")
                f.write(json.dumps(mock_metadata, indent=2))
            
            mock_audios.append(str(mock_audio_path))
        
        return mock_audios
    
    def create_mock_audio(self, text_or_path: str, duration: float = None) -> str:
        """Cria um arquivo de áudio mock individual."""
        # Verificar se o argumento é um caminho de arquivo ou texto
        if os.path.dirname(text_or_path):
            # É um caminho de arquivo
            mock_audio_path = text_or_path
            text = os.path.basename(text_or_path).replace('.mp3', '')
        else:
            # É um texto
            text = text_or_path
            mock_audio_path = self.mock_data_dir / f"mock_audio_{random.randint(1000, 9999)}.mp3"
        
        if duration is None:
            duration = len(text.split()) * 0.5  # ~0.5s por palavra
        
        mock_metadata = {
            "text": text,
            "duration_seconds": duration,
            "generated_at": datetime.now().isoformat(),
            "format": "MP3",
            "_mock": True
        }
        
        # Salvar metadados como arquivo de texto (simulando áudio)
        with open(mock_audio_path, 'w', encoding='utf-8') as f:
            f.write(f"MOCK AUDIO FILE\n")
            f.write(f"Text: {text}\n")
            f.write(f"Duration: {duration:.1f}s\n")
            f.write(json.dumps(mock_metadata, indent=2))
        
        return str(mock_audio_path)
    
    def mock_subtitle_generation(self, audio_files: List[str], word_by_word: bool = False) -> str:
        """Simula geração de legendas pelo Gemini."""
        mock_subtitle_path = self.mock_data_dir / "mock_subtitles.srt"
        
        # Gerar conteúdo SRT mock
        srt_content = []
        current_time = 0.0
        
        if word_by_word:
            # Simular quebra palavra por palavra
            words = ["Teste", "de", "legendas", "palavra", "por", "palavra", "funcionando", "perfeitamente"]
            
            for i, word in enumerate(words):
                start_time = current_time
                end_time = current_time + 0.5  # 0.5s por palavra
                
                srt_block = f"""{i+1}
{self._format_srt_time(start_time)} --> {self._format_srt_time(end_time)}
{word}
"""
                srt_content.append(srt_block)
                current_time = end_time + 0.1  # Pequena pausa
        
        else:
            # Simular legendas normais
            sentences = [
                "Esta é uma legenda de teste.",
                "Gerada automaticamente pelo sistema mock.",
                "Perfeita para validação de funcionalidades."
            ]
            
            for i, sentence in enumerate(sentences):
                start_time = current_time
                end_time = current_time + 3.0  # 3s por frase
                
                srt_block = f"""{i+1}
{self._format_srt_time(start_time)} --> {self._format_srt_time(end_time)}
{sentence}
"""
                srt_content.append(srt_block)
                current_time = end_time + 0.5
        
        # Salvar arquivo SRT
        with open(mock_subtitle_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(srt_content))
        
        return str(mock_subtitle_path)
    
    def _format_srt_time(self, seconds: float) -> str:
        """Formata tempo em formato SRT (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def create_complete_mock_project(self, prompt: str, scenes: int = 3) -> Dict:
        """Cria um projeto completo mock com todos os recursos."""
        print(f"🎭 Gerando projeto mock para: '{prompt}'")
        
        # Gerar script
        script = self.mock_script_generation(prompt, scenes)
        
        # Extrair descrições visuais e narrações
        visual_descriptions = [scene['visual_description'] for scene in script['scenes']]
        narrations = [scene['narration'] for scene in script['scenes']]
        
        # Gerar recursos mock
        images = self.mock_image_generation(visual_descriptions)
        audios = self.mock_audio_generation(narrations)
        subtitles = self.mock_subtitle_generation(audios, word_by_word=True)
        
        # Criar estrutura de projeto
        project_dir = self.mock_data_dir / f"mock_project_{datetime.now().strftime('%H%M%S')}"
        project_dir.mkdir(exist_ok=True)
        
        # Organizar arquivos
        (project_dir / "images").mkdir(exist_ok=True)
        (project_dir / "audio").mkdir(exist_ok=True)
        (project_dir / "subtitles").mkdir(exist_ok=True)
        
        # Mover arquivos para estrutura organizada
        import shutil
        
        organized_resources = {
            'script': str(project_dir / "script.json"),
            'images': [],
            'audios': [],
            'subtitles': str(project_dir / "subtitles" / "subtitles.srt")
        }
        
        # Salvar script
        with open(organized_resources['script'], 'w', encoding='utf-8') as f:
            json.dump(script, f, indent=2, ensure_ascii=False)
        
        # Mover imagens
        for i, img_path in enumerate(images):
            new_path = project_dir / "images" / f"image_{i+1:03d}.png"
            shutil.move(img_path, new_path)
            organized_resources['images'].append(str(new_path))
        
        # Mover áudios
        for i, audio_path in enumerate(audios):
            new_path = project_dir / "audio" / f"audio_scene_{i+1:02d}.mp3"
            shutil.move(audio_path, new_path)
            organized_resources['audios'].append(str(new_path))
        
        # Mover legendas
        shutil.move(subtitles, organized_resources['subtitles'])
        
        # Calcular economia total
        total_savings = (
            len(images) * 0.04 +  # Imagens
            len(audios) * 0.02 +  # Áudios
            0.01 +                # Script
            0.03                  # Legendas
        )
        
        project_info = {
            'project_dir': str(project_dir),
            'resources': organized_resources,
            'total_savings': total_savings,
            'scenes_generated': scenes,
            'created_at': datetime.now().isoformat()
        }
        
        print(f"✅ Projeto mock criado em: {project_dir}")
        print(f"💰 Economia estimada: ${total_savings:.2f}")
        
        return project_info
    
    def generate_mock_report(self) -> str:
        """Gera relatório de uso do sistema mock."""
        mock_files = list(self.mock_data_dir.rglob("*"))
        mock_projects = list(self.mock_data_dir.glob("mock_project_*"))
        
        report = f"""
🎭 RELATÓRIO DO SISTEMA MOCK
{'='*40}

📊 Estatísticas:
   📁 Projetos mock criados: {len(mock_projects)}
   📄 Arquivos mock gerados: {len(mock_files)}
   💾 Diretório mock: {self.mock_data_dir}

🎯 Funcionalidades Simuladas:
   ✅ Geração de scripts (Gemini)
   ✅ Geração de imagens (Gemini Imagen)
   ✅ Geração de áudio (gTTS/ElevenLabs)
   ✅ Geração de legendas (Gemini)

💰 Benefícios:
   • 100% economia em custos de API
   • Testes instantâneos
   • Dados consistentes e reproduzíveis
   • Validação de pipeline completo

⏰ Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return report
    
    def cleanup_mock_data(self, keep_recent: int = 3):
        """Limpa dados mock antigos, mantendo apenas os mais recentes."""
        mock_projects = sorted(
            self.mock_data_dir.glob("mock_project_*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        removed_count = 0
        for project in mock_projects[keep_recent:]:
            import shutil
            shutil.rmtree(project)
            removed_count += 1
        
        print(f"🧹 Limpeza concluída: {removed_count} projetos mock removidos")
        print(f"📁 Mantidos: {min(len(mock_projects), keep_recent)} projetos mais recentes")

# Exemplo de uso
if __name__ == "__main__":
    generator = MockGenerator()
    
    # Criar projeto mock completo
    project = generator.create_complete_mock_project(
        "Um robô explorando uma cidade futurística", 
        scenes=3
    )
    
    print("\n" + generator.generate_mock_report())
    
    # Demonstrar limpeza
    # generator.cleanup_mock_data(keep_recent=2)