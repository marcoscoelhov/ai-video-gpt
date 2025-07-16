#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Teste Unificado - AI Video GPT

Este arquivo consolida todos os testes do sistema em um único local,
reutilizando recursos existentes para economizar créditos de API.

Uso:
    python test_system.py --mode [basic|tiktok|gemini|subtitles|all]
    python test_system.py --reuse  # Reutiliza arquivos existentes
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from main import main as generate_video
from cost_tracker import CostTracker

class TestSystem:
    def __init__(self, reuse_files=False):
        self.reuse_files = reuse_files
        self.test_data_dir = Path("output/test_images")
        self.output_dir = Path("output/tests")
        self.output_dir.mkdir(exist_ok=True)
        
        # Configurações de teste reutilizáveis
        self.test_configs = {
            'basic': {
                'prompt': 'Um gato astronauta explorando uma cidade futurística',
                'duration': 10,
                'format': '16:9'
            },
            'tiktok': {
                'prompt': 'Robô explorando cidade cyberpunk com neon',
                'duration': 15,
                'format': '9:16'
            },
            'gemini': {
                'prompt': 'Fantasia mágica com dragões voando',
                'duration': 12,
                'format': '16:9'
            }
        }
    
    def log_test(self, test_name, status, details=None):
        """Registra resultado do teste"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'test': test_name,
            'status': status,
            'details': details or {}
        }
        
        log_file = self.output_dir / "test_results.json"
        
        # Carrega logs existentes
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        logs.append(log_entry)
        
        # Salva logs atualizados
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        
        print(f"[{timestamp}] {test_name}: {status}")
        if details:
            for key, value in details.items():
                print(f"  {key}: {value}")
    
    def test_basic_video(self):
        """Teste básico de geração de vídeo"""
        print("\n=== Teste Básico de Vídeo ===")
        
        config = self.test_configs['basic']
        output_path = self.output_dir / "basic_test.mp4"
        
        try:
            # Se reutilizar arquivos, verifica se já existe
            if self.reuse_files and output_path.exists():
                self.log_test("basic_video", "REUTILIZADO", {
                    "arquivo": str(output_path),
                    "tamanho": f"{output_path.stat().st_size / 1024 / 1024:.2f} MB"
                })
                return True
            
            # Gera novo vídeo
            result = generate_video(
                prompt=config['prompt'],
                duration=config['duration'],
                output_dir=str(self.output_dir),
                format_type=config['format']
            )
            
            if result and output_path.exists():
                self.log_test("basic_video", "SUCESSO", {
                    "arquivo": str(output_path),
                    "tamanho": f"{output_path.stat().st_size / 1024 / 1024:.2f} MB"
                })
                return True
            else:
                self.log_test("basic_video", "FALHA", {"erro": "Arquivo não gerado"})
                return False
                
        except Exception as e:
            self.log_test("basic_video", "ERRO", {"erro": str(e)})
            return False
    
    def test_tiktok_format(self):
        """Teste específico para formato TikTok (9:16)"""
        print("\n=== Teste Formato TikTok ===")
        
        config = self.test_configs['tiktok']
        output_path = self.output_dir / "tiktok_test.mp4"
        
        try:
            if self.reuse_files and output_path.exists():
                self.log_test("tiktok_format", "REUTILIZADO", {
                    "arquivo": str(output_path),
                    "formato": "9:16",
                    "tamanho": f"{output_path.stat().st_size / 1024 / 1024:.2f} MB"
                })
                return True
            
            result = generate_video(
                prompt=config['prompt'],
                duration=config['duration'],
                output_dir=str(self.output_dir),
                format_type=config['format']
            )
            
            if result and output_path.exists():
                self.log_test("tiktok_format", "SUCESSO", {
                    "arquivo": str(output_path),
                    "formato": "9:16",
                    "tamanho": f"{output_path.stat().st_size / 1024 / 1024:.2f} MB"
                })
                return True
            else:
                self.log_test("tiktok_format", "FALHA", {"erro": "Arquivo não gerado"})
                return False
                
        except Exception as e:
            self.log_test("tiktok_format", "ERRO", {"erro": str(e)})
            return False
    
    def test_gemini_integration(self):
        """Teste de integração com Gemini"""
        print("\n=== Teste Integração Gemini ===")
        
        try:
            # Testa apenas a importação e configuração
            from gemini_imagen_client import GeminiImagenClient
            from src.gemini_subtitle_client import GeminiSubtitleClient
            
            # Verifica se as classes podem ser instanciadas
            imagen_client = GeminiImagenClient()
            subtitle_client = GeminiSubtitleClient()
            
            self.log_test("gemini_integration", "SUCESSO", {
                "imagen_client": "OK",
                "subtitle_client": "OK"
            })
            return True
            
        except Exception as e:
            self.log_test("gemini_integration", "ERRO", {"erro": str(e)})
            return False
    
    def test_subtitle_system(self):
        """Teste do sistema de legendas"""
        print("\n=== Teste Sistema de Legendas ===")
        
        try:
            # Reutiliza arquivo de áudio existente se disponível
            audio_files = list(Path("output").glob("*.mp3"))
            if not audio_files and self.reuse_files:
                self.log_test("subtitle_system", "PULADO", {
                    "motivo": "Nenhum arquivo de áudio encontrado para reutilizar"
                })
                return True
            
            # Testa apenas a importação do sistema de legendas
            from src.gemini_subtitle_client import GeminiSubtitleClient
            
            client = GeminiSubtitleClient()
            
            self.log_test("subtitle_system", "SUCESSO", {
                "client": "Inicializado com sucesso"
            })
            return True
            
        except Exception as e:
            self.log_test("subtitle_system", "ERRO", {"erro": str(e)})
            return False
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("\n🧪 INICIANDO SISTEMA DE TESTES UNIFICADO")
        print(f"Modo de reutilização: {'ATIVADO' if self.reuse_files else 'DESATIVADO'}")
        print("=" * 50)
        
        tests = [
            ("Integração Gemini", self.test_gemini_integration),
            ("Sistema de Legendas", self.test_subtitle_system),
            ("Vídeo Básico", self.test_basic_video),
            ("Formato TikTok", self.test_tiktok_format)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Erro no teste {test_name}: {e}")
                results.append((test_name, False))
        
        # Resumo final
        print("\n" + "=" * 50)
        print("📊 RESUMO DOS TESTES")
        print("=" * 50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"{status} - {test_name}")
        
        print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
        
        if passed == total:
            print("🎉 Todos os testes passaram com sucesso!")
        else:
            print("⚠️  Alguns testes falharam. Verifique os logs para detalhes.")
        
        return passed == total

def main():
    parser = argparse.ArgumentParser(description='Sistema de Teste Unificado')
    parser.add_argument('--mode', choices=['basic', 'tiktok', 'gemini', 'subtitles', 'all'], 
                       default='all', help='Modo de teste')
    parser.add_argument('--reuse', action='store_true', 
                       help='Reutiliza arquivos existentes para economizar créditos')
    
    args = parser.parse_args()
    
    test_system = TestSystem(reuse_files=args.reuse)
    
    if args.mode == 'all':
        success = test_system.run_all_tests()
    elif args.mode == 'basic':
        success = test_system.test_basic_video()
    elif args.mode == 'tiktok':
        success = test_system.test_tiktok_format()
    elif args.mode == 'gemini':
        success = test_system.test_gemini_integration()
    elif args.mode == 'subtitles':
        success = test_system.test_subtitle_system()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()