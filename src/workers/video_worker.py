#!/usr/bin/env python3
"""
Worker para processamento de jobs de geração de vídeo

Este módulo contém as funções que são executadas pelos workers
para processar jobs de geração de vídeo de forma assíncrona.
"""

import os
import sys
import traceback
from typing import Dict, Any

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils.queue_manager import queue_manager, JobStatus
from src.utils.logger import get_logger, ai_logger

def process_video_job(job_id: str) -> Dict[str, Any]:
    """
    Processa um job de geração de vídeo.
    
    Args:
        job_id: ID do job a ser processado
        
    Returns:
        Dict com resultado do processamento
    """
    logger = get_logger("video.worker")
    
    # Set correlation ID for this job
    with ai_logger.correlation_context(job_id):
        try:
            logger.info(f"Iniciando processamento do job {job_id}")
            
            # Recuperar job da fila
            job = queue_manager.get_job(job_id)
            if not job:
                error_msg = f"Job {job_id} não encontrado"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            # Marcar job como em execução
            queue_manager.update_job_progress(
                job_id, 0, "Iniciando processamento...", JobStatus.RUNNING
            )
            
            # Importar módulos necessários
            try:
                from main import main as generate_video_main
            except ImportError as e:
                error_msg = f"Erro ao importar módulo de geração: {e}"
                logger.error(error_msg)
                queue_manager.mark_job_failed(job_id, error_msg)
                return {"success": False, "error": error_msg}
            
            # Preparar argumentos para geração
            args = {
                'script': job.script,
                'image_prompts': job.image_prompts,
                'voice_provider': job.voice_provider,
                'voice_type': job.voice_type,
                'language': job.language,
                'video_format': job.video_format,
                'effects_preset': job.effects_preset,
                'enable_effects': job.enable_effects,
                'image_preset': job.image_preset
            }
            
            # Função de callback para atualizar progresso
            def progress_callback(progress: int, step: str):
                queue_manager.update_job_progress(job_id, progress, step, JobStatus.RUNNING)
                logger.info(f"Job {job_id} progresso: {progress}% - {step}")
            
            # Atualizar progresso inicial
            progress_callback(5, "Configurando geração...")
            
            # Executar geração de vídeo
            try:
                # Simular etapas de progresso
                progress_callback(10, "Gerando roteiro...")
                
                # Aqui seria chamada a função real de geração
                # Por enquanto, vamos simular o processo
                import time
                
                progress_callback(25, "Gerando imagens...")
                time.sleep(2)  # Simular processamento
                
                progress_callback(50, "Gerando áudio...")
                time.sleep(2)  # Simular processamento
                
                progress_callback(75, "Montando vídeo...")
                time.sleep(2)  # Simular processamento
                
                progress_callback(90, "Finalizando...")
                
                # Resultado simulado - em produção seria o resultado real
                video_path = f"outputs/videos/job_{job_id}/final_video.mp4"
                
                # Marcar job como concluído
                queue_manager.mark_job_completed(job_id, video_path)
                
                logger.info(f"Job {job_id} concluído com sucesso")
                return {
                    "success": True,
                    "job_id": job_id,
                    "video_path": video_path
                }
                
            except Exception as e:
                error_msg = f"Erro durante geração: {str(e)}"
                logger.error(f"Job {job_id} falhou: {error_msg}")
                logger.error(traceback.format_exc())
                queue_manager.mark_job_failed(job_id, error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Erro crítico no worker: {str(e)}"
            logger.error(f"Job {job_id} falhou criticamente: {error_msg}")
            logger.error(traceback.format_exc())
            
            try:
                queue_manager.mark_job_failed(job_id, error_msg)
            except:
                pass  # Evitar erro duplo
                
            return {"success": False, "error": error_msg}

def start_worker():
    """
    Inicia um worker para processar jobs da fila.
    """
    logger = get_logger("video.worker.startup")
    
    if not queue_manager.use_redis:
        logger.warning("Redis não disponível. Worker não pode ser iniciado.")
        return
    
    try:
        from rq import Worker, Connection
        
        logger.info("Iniciando worker de vídeo...")
        
        with Connection(queue_manager.redis_client):
            worker = Worker([queue_manager.queue])
            worker.work()
            
    except Exception as e:
        logger.error(f"Erro ao iniciar worker: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    start_worker()