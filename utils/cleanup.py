#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Limpeza Automática - AI Video GPT

Gerencia arquivos temporários, relatórios antigos e otimiza o espaço em disco.

Uso:
    python cleanup.py --auto     # Limpeza automática (segura)
    python cleanup.py --deep     # Limpeza profunda
    python cleanup.py --reports  # Apenas relatórios antigos
    python cleanup.py --dry-run  # Simula limpeza sem deletar
"""

import os
import sys
import json
import argparse
import shutil
from pathlib import Path
from datetime import datetime, timedelta

class CleanupSystem:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.project_root = Path(".")
        self.output_dir = Path("output")
        
        # Configurações de limpeza
        self.cleanup_config = {
            'keep_reports': 5,  # Manter apenas os 5 relatórios mais recentes
            'keep_videos': 3,   # Manter apenas os 3 vídeos mais recentes
            'max_age_days': 7,  # Arquivos temporários mais antigos que 7 dias
            'temp_extensions': ['.tmp', '.temp', '.cache'],
            'log_extensions': ['.log']
        }
        
        self.stats = {
            'files_removed': 0,
            'dirs_removed': 0,
            'space_freed': 0
        }
    
    def log_action(self, action, path, size=0):
        """Registra ação de limpeza"""
        if self.dry_run:
            print(f"[DRY-RUN] {action}: {path}")
        else:
            print(f"[CLEANUP] {action}: {path}")
            
        if not self.dry_run:
            self.stats['space_freed'] += size
    
    def get_file_age_days(self, file_path):
        """Retorna idade do arquivo em dias"""
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            return (datetime.now() - mtime).days
        except:
            return 0
    
    def cleanup_cost_reports(self):
        """Limpa relatórios de custo antigos"""
        print("\n🧹 Limpando relatórios de custo antigos...")
        
        # Encontra todos os relatórios de custo
        report_files = []
        
        # Relatórios no diretório raiz
        for pattern in ['cost_report_*.json', 'cost_*.json']:
            report_files.extend(self.project_root.glob(pattern))
        
        # Relatórios no diretório output
        if self.output_dir.exists():
            for pattern in ['cost_report_*.json', 'cost_*.json']:
                report_files.extend(self.output_dir.glob(pattern))
            
            # Relatórios em subdiretórios
            for subdir in self.output_dir.iterdir():
                if subdir.is_dir():
                    for pattern in ['cost_report_*.json', 'cost_*.json']:
                        report_files.extend(subdir.glob(pattern))
        
        if not report_files:
            print("📊 Nenhum relatório de custo encontrado")
            return
        
        # Ordena por data de modificação (mais recente primeiro)
        report_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Mantém apenas os mais recentes
        keep_count = self.cleanup_config['keep_reports']
        to_remove = report_files[keep_count:]
        
        print(f"📊 Encontrados {len(report_files)} relatórios")
        print(f"📌 Mantendo {min(len(report_files), keep_count)} mais recentes")
        
        for report_file in to_remove:
            size = report_file.stat().st_size
            self.log_action("Removendo relatório", report_file, size)
            
            if not self.dry_run:
                report_file.unlink()
                self.stats['files_removed'] += 1
    
    def cleanup_old_projects(self):
        """Limpa projetos de teste antigos"""
        print("\n🗂️  Limpando projetos antigos...")
        
        if not self.output_dir.exists():
            return
        
        # Encontra diretórios de projetos antigos
        project_dirs = []
        for item in self.output_dir.iterdir():
            if item.is_dir() and item.name.startswith('video_'):
                age_days = self.get_file_age_days(item)
                if age_days > self.cleanup_config['max_age_days']:
                    project_dirs.append((item, age_days))
        
        if not project_dirs:
            print("📁 Nenhum projeto antigo encontrado")
            return
        
        print(f"📁 Encontrados {len(project_dirs)} projetos antigos")
        
        for project_dir, age in project_dirs:
            # Calcula tamanho do diretório
            size = sum(f.stat().st_size for f in project_dir.rglob('*') if f.is_file())
            
            self.log_action(f"Removendo projeto ({age} dias)", project_dir, size)
            
            if not self.dry_run:
                shutil.rmtree(project_dir)
                self.stats['dirs_removed'] += 1
    
    def cleanup_temp_files(self):
        """Limpa arquivos temporários"""
        print("\n🗑️  Limpando arquivos temporários...")
        
        temp_files = []
        
        # Busca arquivos temporários
        for ext in self.cleanup_config['temp_extensions']:
            temp_files.extend(self.project_root.rglob(f'*{ext}'))
        
        # Busca logs antigos
        for ext in self.cleanup_config['log_extensions']:
            log_files = self.project_root.rglob(f'*{ext}')
            for log_file in log_files:
                if self.get_file_age_days(log_file) > self.cleanup_config['max_age_days']:
                    temp_files.append(log_file)
        
        if not temp_files:
            print("🗑️  Nenhum arquivo temporário encontrado")
            return
        
        print(f"🗑️  Encontrados {len(temp_files)} arquivos temporários")
        
        for temp_file in temp_files:
            size = temp_file.stat().st_size
            self.log_action("Removendo temporário", temp_file, size)
            
            if not self.dry_run:
                temp_file.unlink()
                self.stats['files_removed'] += 1
    
    def cleanup_old_videos(self):
        """Limpa vídeos antigos mantendo apenas os mais recentes"""
        print("\n🎬 Gerenciando vídeos antigos...")
        
        if not self.output_dir.exists():
            return
        
        # Encontra todos os vídeos
        video_files = []
        for ext in ['.mp4', '.avi', '.mov', '.mkv']:
            video_files.extend(self.output_dir.rglob(f'*{ext}'))
        
        if not video_files:
            print("🎬 Nenhum vídeo encontrado")
            return
        
        # Ordena por data de modificação (mais recente primeiro)
        video_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Mantém apenas os mais recentes
        keep_count = self.cleanup_config['keep_videos']
        to_remove = video_files[keep_count:]
        
        print(f"🎬 Encontrados {len(video_files)} vídeos")
        print(f"📌 Mantendo {min(len(video_files), keep_count)} mais recentes")
        
        for video_file in to_remove:
            size = video_file.stat().st_size
            self.log_action("Removendo vídeo antigo", video_file, size)
            
            if not self.dry_run:
                video_file.unlink()
                self.stats['files_removed'] += 1
    
    def optimize_structure(self):
        """Otimiza estrutura de diretórios"""
        print("\n📁 Otimizando estrutura...")
        
        # Remove diretórios vazios
        empty_dirs = []
        
        if self.output_dir.exists():
            for item in self.output_dir.rglob('*'):
                if item.is_dir() and not any(item.iterdir()):
                    empty_dirs.append(item)
        
        if empty_dirs:
            print(f"📁 Encontrados {len(empty_dirs)} diretórios vazios")
            
            for empty_dir in empty_dirs:
                self.log_action("Removendo diretório vazio", empty_dir)
                
                if not self.dry_run:
                    empty_dir.rmdir()
                    self.stats['dirs_removed'] += 1
        else:
            print("📁 Nenhum diretório vazio encontrado")
    
    def generate_cleanup_report(self):
        """Gera relatório de limpeza"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': self.dry_run,
            'stats': self.stats,
            'config': self.cleanup_config
        }
        
        report_file = self.output_dir / "cleanup_report.json"
        
        if not self.dry_run:
            self.output_dir.mkdir(exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def run_auto_cleanup(self):
        """Executa limpeza automática (segura)"""
        print("🧹 LIMPEZA AUTOMÁTICA")
        print("=" * 40)
        
        self.cleanup_cost_reports()
        self.cleanup_temp_files()
        self.optimize_structure()
        
        self.print_summary()
    
    def run_deep_cleanup(self):
        """Executa limpeza profunda"""
        print("🧹 LIMPEZA PROFUNDA")
        print("=" * 40)
        
        self.cleanup_cost_reports()
        self.cleanup_old_projects()
        self.cleanup_temp_files()
        self.cleanup_old_videos()
        self.optimize_structure()
        
        self.print_summary()
    
    def run_reports_only(self):
        """Limpa apenas relatórios"""
        print("📊 LIMPEZA DE RELATÓRIOS")
        print("=" * 40)
        
        self.cleanup_cost_reports()
        
        self.print_summary()
    
    def print_summary(self):
        """Imprime resumo da limpeza"""
        print("\n" + "=" * 40)
        print("📊 RESUMO DA LIMPEZA")
        print("=" * 40)
        
        if self.dry_run:
            print("⚠️  MODO SIMULAÇÃO - Nenhum arquivo foi removido")
        
        print(f"🗑️  Arquivos removidos: {self.stats['files_removed']}")
        print(f"📁 Diretórios removidos: {self.stats['dirs_removed']}")
        
        space_mb = self.stats['space_freed'] / 1024 / 1024
        print(f"💾 Espaço liberado: {space_mb:.2f} MB")
        
        if not self.dry_run and (self.stats['files_removed'] > 0 or self.stats['dirs_removed'] > 0):
            report = self.generate_cleanup_report()
            print(f"📋 Relatório salvo em: output/cleanup_report.json")
        
        print("\n✅ Limpeza concluída!")

def main():
    parser = argparse.ArgumentParser(description='Sistema de Limpeza Automática')
    parser.add_argument('--auto', action='store_true', 
                       help='Limpeza automática (segura)')
    parser.add_argument('--deep', action='store_true', 
                       help='Limpeza profunda')
    parser.add_argument('--reports', action='store_true', 
                       help='Apenas relatórios antigos')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Simula limpeza sem deletar arquivos')
    
    args = parser.parse_args()
    
    cleanup_system = CleanupSystem(dry_run=args.dry_run)
    
    if args.reports:
        cleanup_system.run_reports_only()
    elif args.deep:
        cleanup_system.run_deep_cleanup()
    else:
        cleanup_system.run_auto_cleanup()

if __name__ == "__main__":
    main()