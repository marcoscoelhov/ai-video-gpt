#!/usr/bin/env python3
"""
Testes unitários para o QueueManager
"""

import unittest
import os
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Adicionar o diretório src ao path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.queue_manager import QueueManager, VideoJob, JobStatus

class TestVideoJob(unittest.TestCase):
    """Testes para a classe VideoJob"""
    
    def test_video_job_creation(self):
        """Testa criação de um VideoJob"""
        job = VideoJob(
            job_id="test-123",
            script="Teste de script",
            image_prompts=["prompt1", "prompt2"]
        )
        
        self.assertEqual(job.job_id, "test-123")
        self.assertEqual(job.script, "Teste de script")
        self.assertEqual(job.image_prompts, ["prompt1", "prompt2"])
        self.assertEqual(job.status, JobStatus.PENDING)
        self.assertEqual(job.progress, 0)
        self.assertIsNotNone(job.created_at)
    
    def test_video_job_to_dict(self):
        """Testa conversão de VideoJob para dicionário"""
        job = VideoJob(
            job_id="test-123",
            script="Teste",
            image_prompts=["prompt1"]
        )
        
        job_dict = job.to_dict()
        
        self.assertIsInstance(job_dict, dict)
        self.assertEqual(job_dict['job_id'], "test-123")
        self.assertEqual(job_dict['status'], "pending")
        self.assertIsInstance(job_dict['created_at'], str)
    
    def test_video_job_from_dict(self):
        """Testa criação de VideoJob a partir de dicionário"""
        job_data = {
            'job_id': 'test-123',
            'script': 'Teste',
            'image_prompts': ['prompt1'],
            'status': 'pending',
            'progress': 0,
            'current_step': 'Iniciando...',
            'created_at': datetime.now().isoformat()
        }
        
        job = VideoJob.from_dict(job_data)
        
        self.assertEqual(job.job_id, "test-123")
        self.assertEqual(job.status, JobStatus.PENDING)
        self.assertIsInstance(job.created_at, datetime)

class TestQueueManager(unittest.TestCase):
    """Testes para a classe QueueManager"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        # Forçar uso de sistema em memória para testes
        with patch.dict(os.environ, {'USE_REDIS': 'false'}):
            self.queue_manager = QueueManager()
    
    def test_queue_manager_initialization(self):
        """Testa inicialização do QueueManager"""
        self.assertFalse(self.queue_manager.use_redis)
        self.assertIsInstance(self.queue_manager.memory_jobs, dict)
        self.assertEqual(len(self.queue_manager.memory_jobs), 0)
    
    def test_create_job(self):
        """Testa criação de job"""
        job_id = self.queue_manager.create_job(
            script="Teste de script",
            image_prompts=["prompt1", "prompt2"]
        )
        
        self.assertIsInstance(job_id, str)
        self.assertIn(job_id, self.queue_manager.memory_jobs)
        
        job = self.queue_manager.memory_jobs[job_id]
        self.assertEqual(job.script, "Teste de script")
        self.assertEqual(job.image_prompts, ["prompt1", "prompt2"])
    
    def test_get_job(self):
        """Testa recuperação de job"""
        job_id = self.queue_manager.create_job(
            script="Teste",
            image_prompts=["prompt1"]
        )
        
        retrieved_job = self.queue_manager.get_job(job_id)
        
        self.assertIsNotNone(retrieved_job)
        self.assertEqual(retrieved_job.job_id, job_id)
        self.assertEqual(retrieved_job.script, "Teste")
    
    def test_get_nonexistent_job(self):
        """Testa recuperação de job inexistente"""
        job = self.queue_manager.get_job("nonexistent-id")
        self.assertIsNone(job)
    
    def test_queue_job(self):
        """Testa enfileiramento de job"""
        job_id = self.queue_manager.create_job(
            script="Teste",
            image_prompts=["prompt1"]
        )
        
        success = self.queue_manager.queue_job(job_id)
        
        self.assertTrue(success)
        job = self.queue_manager.get_job(job_id)
        self.assertEqual(job.status, JobStatus.QUEUED)
    
    def test_update_job_progress(self):
        """Testa atualização de progresso do job"""
        job_id = self.queue_manager.create_job(
            script="Teste",
            image_prompts=["prompt1"]
        )
        
        success = self.queue_manager.update_job_progress(
            job_id, 50, "Processando...", JobStatus.RUNNING
        )
        
        self.assertTrue(success)
        job = self.queue_manager.get_job(job_id)
        self.assertEqual(job.progress, 50)
        self.assertEqual(job.current_step, "Processando...")
        self.assertEqual(job.status, JobStatus.RUNNING)
        self.assertIsNotNone(job.started_at)
    
    def test_mark_job_completed(self):
        """Testa marcação de job como concluído"""
        job_id = self.queue_manager.create_job(
            script="Teste",
            image_prompts=["prompt1"]
        )
        
        success = self.queue_manager.mark_job_completed(job_id, "video_url_test")
        
        self.assertTrue(success)
        job = self.queue_manager.get_job(job_id)
        self.assertEqual(job.status, JobStatus.COMPLETED)
        self.assertEqual(job.video_url, "video_url_test")
        self.assertIsNotNone(job.completed_at)
    
    def test_mark_job_failed(self):
        """Testa marcação de job como falhou"""
        job_id = self.queue_manager.create_job(
            script="Teste",
            image_prompts=["prompt1"]
        )
        
        success = self.queue_manager.mark_job_failed(job_id, "Erro de teste")
        
        self.assertTrue(success)
        job = self.queue_manager.get_job(job_id)
        self.assertEqual(job.status, JobStatus.FAILED)
        self.assertEqual(job.error_message, "Erro de teste")
    
    def test_get_queue_length(self):
        """Testa obtenção do tamanho da fila"""
        initial_length = self.queue_manager.get_queue_length()
        
        job_id = self.queue_manager.create_job(
            script="Teste",
            image_prompts=["prompt1"]
        )
        self.queue_manager.queue_job(job_id)
        
        new_length = self.queue_manager.get_queue_length()
        self.assertEqual(new_length, initial_length + 1)
    
    def test_get_job_position(self):
        """Testa obtenção da posição do job na fila"""
        job_id = self.queue_manager.create_job(
            script="Teste",
            image_prompts=["prompt1"]
        )
        self.queue_manager.queue_job(job_id)
        
        position = self.queue_manager.get_job_position(job_id)
        self.assertIsInstance(position, int)
        self.assertGreaterEqual(position, 0)
    
    def test_list_jobs(self):
        """Testa listagem de jobs"""
        # Criar alguns jobs
        job_ids = []
        for i in range(3):
            job_id = self.queue_manager.create_job(
                script=f"Teste {i}",
                image_prompts=[f"prompt{i}"]
            )
            job_ids.append(job_id)
            self.queue_manager.queue_job(job_id)
        
        jobs = self.queue_manager.list_jobs()
        
        self.assertIsInstance(jobs, list)
        self.assertEqual(len(jobs), 3)
        
        # Verificar se todos os jobs estão na lista
        job_ids_in_list = [job.job_id for job in jobs]
        for job_id in job_ids:
            self.assertIn(job_id, job_ids_in_list)

if __name__ == '__main__':
    unittest.main()