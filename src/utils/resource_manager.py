#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resource Manager - Sistema de Reutilização de Recursos

Este módulo gerencia a reutilização de recursos já gerados (imagens, áudios, scripts)
para economizar custos de API e acelerar testes.

Autor: AI Video GPT
Data: 2025-01-19
"""

import os
import json
import random
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import shutil
from datetime import datetime

class ResourceManager:
    """Gerenciador de recursos existentes para reutilização em testes."""
    
    def __init__(self, outputs_dir: str = "outputs"):
        self.outputs_dir = Path(outputs_dir)
        self.videos_dir = self.outputs_dir / "videos"
        self.images_dir = self.outputs_dir / "images"
        self.demos_dir = self.outputs_dir / "demos"
        
        # Estatísticas de uso
        self.stats = {
            'images_reused': 0,
            'audios_reused': 0,
            'scripts_reused': 0,
            'total_savings': 0.0
        }
    
    def scan_available_resources(self) -> Dict:
        """Escaneia todos os recursos disponíveis para reutilização."""
        resources = {
            'videos': [],
            'images': [],
            'audios': [],
            'scripts': [],
            'subtitles': []
        }
        
        print("🔍 Escaneando recursos disponíveis...")
        
        # Escanear vídeos completos
        if self.videos_dir.exists():
            for video_dir in self.videos_dir.iterdir():
                if video_dir.is_dir():
                    video_info = self._analyze_video_directory(video_dir)
                    if video_info:
                        resources['videos'].append(video_info)
        
        # Escanear imagens avulsas
        if self.images_dir.exists():
            for img_file in self.images_dir.rglob("*.png"):
                resources['images'].append({
                    'path': str(img_file),
                    'size_kb': img_file.stat().st_size / 1024,
                    'type': 'standalone'
                })
        
        # Escanear demos
        if self.demos_dir.exists():
            for demo_dir in self.demos_dir.iterdir():
                if demo_dir.is_dir():
                    demo_info = self._analyze_video_directory(demo_dir)
                    if demo_info:
                        resources['videos'].append(demo_info)
        
        print(f"📊 Recursos encontrados:")
        print(f"   🎬 Vídeos completos: {len(resources['videos'])}")
        print(f"   🖼️  Imagens: {len(resources['images'])}")
        
        return resources
    
    def _analyze_video_directory(self, video_dir: Path) -> Optional[Dict]:
        """Analisa um diretório de vídeo e extrai informações dos recursos."""
        try:
            info = {
                'name': video_dir.name,
                'path': str(video_dir),
                'images': [],
                'audios': [],
                'script': None,
                'subtitles': None,
                'video_file': None
            }
            
            # Buscar imagens
            images_dir = video_dir / "images"
            if images_dir.exists():
                for img in images_dir.glob("*.png"):
                    info['images'].append({
                        'path': str(img),
                        'size_kb': img.stat().st_size / 1024
                    })
            
            # Buscar áudios
            audio_dir = video_dir / "audio"
            if audio_dir.exists():
                for audio in audio_dir.glob("*.mp3"):
                    info['audios'].append({
                        'path': str(audio),
                        'size_kb': audio.stat().st_size / 1024
                    })
            
            # Buscar script
            script_file = video_dir / "script.json"
            if script_file.exists():
                info['script'] = str(script_file)
            
            # Buscar legendas
            subtitles_dir = video_dir / "subtitles"
            if subtitles_dir.exists():
                srt_file = subtitles_dir / "subtitles.srt"
                if srt_file.exists():
                    info['subtitles'] = str(srt_file)
            
            # Buscar vídeo final
            for video_file in video_dir.glob("*.mp4"):
                info['video_file'] = str(video_file)
                break
            
            # Só retorna se tiver pelo menos imagens ou áudios
            if info['images'] or info['audios']:
                return info
            
        except Exception as e:
            print(f"⚠️  Erro ao analisar {video_dir}: {e}")
        
        return None
    
    def get_random_resources(self, count: int = 3) -> Dict:
        """Obtém recursos aleatórios para reutilização."""
        resources = self.scan_available_resources()
        
        if not resources['videos']:
            print("❌ Nenhum recurso de vídeo encontrado!")
            return None
        
        # Selecionar vídeo aleatório
        selected_video = random.choice(resources['videos'])
        
        # Extrair recursos necessários
        result = {
            'source_video': selected_video['name'],
            'images': selected_video['images'][:count],
            'audios': selected_video['audios'][:count],
            'script': selected_video['script'],
            'subtitles': selected_video['subtitles']
        }
        
        print(f"🎲 Recursos selecionados de: {selected_video['name']}")
        print(f"   🖼️  Imagens: {len(result['images'])}")
        print(f"   🎵 Áudios: {len(result['audios'])}")
        
        return result
    
    def copy_resources_to_test_dir(self, resources: Dict, test_dir: Path) -> Dict:
        """Copia recursos selecionados para diretório de teste."""
        test_dir.mkdir(exist_ok=True)
        
        # Criar estrutura de diretórios
        (test_dir / "images").mkdir(exist_ok=True)
        (test_dir / "audio").mkdir(exist_ok=True)
        (test_dir / "subtitles").mkdir(exist_ok=True)
        
        copied_resources = {
            'images': [],
            'audios': [],
            'script': None,
            'subtitles': None
        }
        
        # Copiar imagens
        for i, img_info in enumerate(resources['images']):
            src_path = Path(img_info['path'])
            dst_path = test_dir / "images" / f"image_{i+1:03d}.png"
            shutil.copy2(src_path, dst_path)
            copied_resources['images'].append(str(dst_path))
            self.stats['images_reused'] += 1
        
        # Copiar áudios
        for i, audio_info in enumerate(resources['audios']):
            src_path = Path(audio_info['path'])
            dst_path = test_dir / "audio" / f"audio_scene_{i+1:02d}.mp3"
            shutil.copy2(src_path, dst_path)
            copied_resources['audios'].append(str(dst_path))
            self.stats['audios_reused'] += 1
        
        # Copiar script
        if resources['script']:
            src_path = Path(resources['script'])
            dst_path = test_dir / "script.json"
            shutil.copy2(src_path, dst_path)
            copied_resources['script'] = str(dst_path)
            self.stats['scripts_reused'] += 1
        
        # Copiar legendas
        if resources['subtitles']:
            src_path = Path(resources['subtitles'])
            dst_path = test_dir / "subtitles" / "subtitles.srt"
            shutil.copy2(src_path, dst_path)
            copied_resources['subtitles'] = str(dst_path)
        
        print(f"📁 Recursos copiados para: {test_dir}")
        return copied_resources
    
    def create_mock_script(self, prompt: str, scenes: int = 3) -> Dict:
        """Cria um script mock baseado em um prompt."""
        mock_script = {
            "theme": prompt,
            "title": f"Teste: {prompt.title()}",
            "scenes": []
        }
        
        # Descrições visuais genéricas para teste
        visual_templates = [
            "Close-up shot with dramatic lighting and vibrant colors",
            "Wide establishing shot with cinematic composition",
            "Dynamic action scene with motion blur effects",
            "Atmospheric scene with moody lighting",
            "Detailed macro shot with shallow depth of field"
        ]
        
        # Narrações genéricas para teste
        narration_templates = [
            "Uma jornada começa.",
            "O mistério se aprofunda.",
            "A aventura continua.",
            "Descobertas surpreendentes.",
            "O final se aproxima."
        ]
        
        for i in range(scenes):
            scene = {
                "scene": i + 1,
                "visual_description": f"{prompt} - {random.choice(visual_templates)}",
                "narration": random.choice(narration_templates)
            }
            mock_script["scenes"].append(scene)
        
        return mock_script
    
    def estimate_savings(self, resources_used: Dict) -> float:
        """Estima a economia de custos ao reutilizar recursos."""
        # Custos estimados por recurso (em USD)
        costs = {
            'image_generation': 0.04,  # Por imagem Gemini
            'audio_generation': 0.02,  # Por áudio gTTS/ElevenLabs
            'script_generation': 0.01,  # Por script Gemini
            'subtitle_generation': 0.03  # Por legenda Gemini
        }
        
        savings = 0.0
        savings += len(resources_used.get('images', [])) * costs['image_generation']
        savings += len(resources_used.get('audios', [])) * costs['audio_generation']
        
        if resources_used.get('script'):
            savings += costs['script_generation']
        
        if resources_used.get('subtitles'):
            savings += costs['subtitle_generation']
        
        self.stats['total_savings'] += savings
        return savings
    
    def generate_usage_report(self) -> str:
        """Gera relatório de uso dos recursos reutilizados."""
        report = f"""
🧪 RELATÓRIO DE REUTILIZAÇÃO DE RECURSOS
{'='*50}

📊 Estatísticas de Uso:
   🖼️  Imagens reutilizadas: {self.stats['images_reused']}
   🎵 Áudios reutilizados: {self.stats['audios_reused']}
   📝 Scripts reutilizados: {self.stats['scripts_reused']}
   💰 Economia total estimada: ${self.stats['total_savings']:.2f}

⏰ Data do relatório: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ Benefícios da Reutilização:
   • Redução de 90%+ nos custos de API
   • Testes 5x mais rápidos
   • Foco na validação de funcionalidades
   • Testes repetíveis e consistentes
"""
        return report

# Exemplo de uso
if __name__ == "__main__":
    manager = ResourceManager()
    
    # Escanear recursos
    resources = manager.scan_available_resources()
    
    # Obter recursos aleatórios
    selected = manager.get_random_resources(3)
    
    if selected:
        # Criar diretório de teste
        test_dir = Path("test_reuse_demo")
        
        # Copiar recursos
        copied = manager.copy_resources_to_test_dir(selected, test_dir)
        
        # Calcular economia
        savings = manager.estimate_savings(copied)
        
        print(f"\n💰 Economia estimada: ${savings:.2f}")
        print(manager.generate_usage_report())
    else:
        print("❌ Nenhum recurso disponível para reutilização!")