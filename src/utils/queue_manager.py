#!/usr/bin/env python3
"""
Sistema de Filas com Redis para AI Video GPT

Este módulo implementa um sistema de filas persistente usando Redis
para gerenciar jobs de geração de vídeo de forma escalável.
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import redis
    from rq import Queue, Worker, Connection
    from rq.job import Job
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis não disponível. Usando sistema em memória.")

from .logger import get_logger

class JobStatus(Enum):
    """Status possíveis para jobs"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class VideoJob:
    """Classe para representar um job de geração de vídeo"""
    job_id: str
    script: str
    image_prompts: List[str]
    voice_provider: str = 'auto'
    voice_type: str = 'narrator'
    language: str = 'pt'
    video_format: str = 'standard'
    effects_preset: str = 'professional'
    enable_effects: bool = True
    image_preset: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    progress: int = 0
    current_step: str = 'Iniciando...'
    error_message: Optional[str] = None
    video_path: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o job para dicionário"""
        data = asdict(self)
        # Converter enums e datetime para strings
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['started_at'] = self.started_at.isoformat() if self.started_at else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoJob':
        """Cria um job a partir de dicionário"""
        # Converter strings de volta para objetos
        if 'status' in data:
            data['status'] = JobStatus(data['status'])
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'started_at' in data and data['started_at']:
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if 'completed_at' in data and data['completed_at']:
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        if 'updated_at' in data and data['updated_at']:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)

class QueueManager:
    """Gerenciador de filas com Redis"""
    
    def __init__(self):
        self.logger = get_logger("queue.manager")
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.use_redis = REDIS_AVAILABLE and os.getenv('USE_REDIS', 'true').lower() == 'true'
        
        # Fallback para sistema em memória
        self.memory_jobs: Dict[str, VideoJob] = {}
        
        if self.use_redis:
            try:
                self.redis_client = redis.from_url(self.redis_url)
                self.queue = Queue('video_generation', connection=self.redis_client)
                self.redis_client.ping()  # Testar conexão
                self.logger.info("Redis conectado com sucesso")
            except Exception as e:
                self.logger.warning(f"Falha ao conectar Redis: {e}. Usando sistema em memória.")
                self.use_redis = False
                self.redis_client = None
                self.queue = None
        else:
            self.redis_client = None
            self.queue = None
            self.logger.info("Usando sistema de filas em memória")
    
    def create_job(self, script: str, image_prompts: List[str], **kwargs) -> str:
        """Cria um novo job de geração de vídeo"""
        job_id = str(uuid.uuid4())
        
        job = VideoJob(
            job_id=job_id,
            script=script,
            image_prompts=image_prompts,
            **kwargs
        )
        
        if self.use_redis:
            # Salvar job no Redis
            self.redis_client.hset(
                f"job:{job_id}",
                mapping={
                    "data": json.dumps(job.to_dict()),
                    "created_at": job.created_at.isoformat()
                }
            )
            # Definir TTL de 24 horas
            self.redis_client.expire(f"job:{job_id}", 86400)
        else:
            # Salvar em memória
            self.memory_jobs[job_id] = job
        
        self.logger.info(f"Job criado: {job_id}")
        return job_id
    
    def queue_job(self, job_id: str, timeout: int = 3600) -> bool:
        """Adiciona job à fila de processamento"""
        try:
            job = self.get_job(job_id)
            if not job:
                return False
            
            if self.use_redis:
                # Enfileirar no Redis Queue
                rq_job = self.queue.enqueue(
                    'src.workers.video_worker.process_video_job',
                    job_id,
                    timeout=timeout,
                    job_id=job_id
                )
                job.status = JobStatus.QUEUED
                self.update_job(job)
                self.logger.info(f"Job enfileirado no Redis: {job_id}")
            else:
                # Para sistema em memória, marcar como enfileirado
                job.status = JobStatus.QUEUED
                self.memory_jobs[job_id] = job
                self.logger.info(f"Job enfileirado em memória: {job_id}")
            
            return True
        except Exception as e:
            self.logger.error(f"Erro ao enfileirar job {job_id}: {e}")
            return False
    
    def get_job(self, job_id: str) -> Optional[VideoJob]:
        """Recupera um job pelo ID"""
        try:
            if self.use_redis:
                data = self.redis_client.hget(f"job:{job_id}", "data")
                if data:
                    job_data = json.loads(data)
                    return VideoJob.from_dict(job_data)
            else:
                return self.memory_jobs.get(job_id)
        except Exception as e:
            self.logger.error(f"Erro ao recuperar job {job_id}: {e}")
        return None
    
    def update_job(self, job: VideoJob) -> bool:
        """Atualiza um job existente"""
        try:
            # Definir updated_at
            job.updated_at = datetime.now()
            
            if self.use_redis:
                self.redis_client.hset(
                    f"job:{job.job_id}",
                    mapping={
                        "data": json.dumps(job.to_dict()),
                        "updated_at": job.updated_at.isoformat()
                    }
                )
            else:
                self.memory_jobs[job.job_id] = job
            
            return True
        except Exception as e:
            self.logger.error(f"Erro ao atualizar job {job.job_id}: {e}")
            return False
    
    def update_job_progress(self, job_id: str, progress: int, step: str, status: JobStatus = None) -> bool:
        """Atualiza o progresso de um job"""
        job = self.get_job(job_id)
        if not job:
            return False
        
        job.progress = progress
        job.current_step = step
        if status:
            job.status = status
            if status == JobStatus.RUNNING and not job.started_at:
                job.started_at = datetime.now()
            elif status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                job.completed_at = datetime.now()
        
        return self.update_job(job)
    
    def mark_job_completed(self, job_id: str, video_path: str) -> bool:
        """Marca um job como concluído"""
        job = self.get_job(job_id)
        if not job:
            return False
        
        job.status = JobStatus.COMPLETED
        job.video_path = video_path
        job.progress = 100
        job.current_step = "Concluído"
        job.completed_at = datetime.now()
        
        return self.update_job(job)
    
    def mark_job_failed(self, job_id: str, error_message: str) -> bool:
        """Marca um job como falhado"""
        job = self.get_job(job_id)
        if not job:
            return False
        
        job.status = JobStatus.FAILED
        job.error_message = error_message
        job.completed_at = datetime.now()
        
        return self.update_job(job)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Retorna status da fila"""
        if self.use_redis:
            try:
                queue_length = len(self.queue)
                failed_jobs = len(self.queue.failed_job_registry)
                return {
                    "type": "redis",
                    "queue_length": queue_length,
                    "failed_jobs": failed_jobs,
                    "workers": len(Worker.all(connection=self.redis_client))
                }
            except Exception as e:
                self.logger.error(f"Erro ao obter status da fila: {e}")
                return {"type": "redis", "error": str(e)}
        else:
            pending_jobs = len([j for j in self.memory_jobs.values() if j.status == JobStatus.QUEUED])
            return {
                "type": "memory",
                "queue_length": pending_jobs,
                "total_jobs": len(self.memory_jobs)
            }
    
    def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """Remove jobs antigos"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        removed_count = 0
        
        if self.use_redis:
            # Redis TTL já cuida da limpeza automática
            return 0
        else:
            # Limpar jobs em memória
            jobs_to_remove = [
                job_id for job_id, job in self.memory_jobs.items()
                if job.created_at < cutoff_time and job.status in [JobStatus.COMPLETED, JobStatus.FAILED]
            ]
            
            for job_id in jobs_to_remove:
                del self.memory_jobs[job_id]
                removed_count += 1
        
        self.logger.info(f"Removidos {removed_count} jobs antigos")
        return removed_count
    
    def get_queue_length(self) -> int:
        """Retorna o número de jobs na fila"""
        if self.use_redis:
            try:
                return len(self.queue)
            except Exception as e:
                self.logger.error(f"Erro ao obter tamanho da fila: {e}")
                return 0
        else:
            return len([j for j in self.memory_jobs.values() if j.status == JobStatus.QUEUED])
    
    def get_job_position(self, job_id: str) -> Optional[int]:
        """Retorna a posição do job na fila (apenas para Redis)"""
        if not self.use_redis:
            return None
        
        try:
            # Para Redis, seria necessário implementar lógica específica
            # Por enquanto, retorna None
            return None
        except Exception as e:
            self.logger.error(f"Erro ao obter posição do job {job_id}: {e}")
            return None
    
    def list_jobs(self) -> List[VideoJob]:
        """Lista todos os jobs"""
        if self.use_redis:
            try:
                # Buscar todas as chaves de jobs no Redis
                job_keys = self.redis_client.keys("job:*")
                jobs = []
                for key in job_keys:
                    data = self.redis_client.hget(key, "data")
                    if data:
                        job_data = json.loads(data)
                        jobs.append(VideoJob.from_dict(job_data))
                return jobs
            except Exception as e:
                self.logger.error(f"Erro ao listar jobs: {e}")
                return []
        else:
            return list(self.memory_jobs.values())

# Instância global do gerenciador de filas
queue_manager = QueueManager()