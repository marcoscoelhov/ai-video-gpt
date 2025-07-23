#!/usr/bin/env python3
"""
Script para iniciar workers de processamento de vídeo

Este script inicia workers que processam jobs de geração de vídeo
da fila Redis de forma assíncrona.
"""

import os
import sys
import signal
import argparse
from typing import List

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(__file__))

from src.utils.logger import get_logger, ai_logger
from src.utils.queue_manager import queue_manager
from src.workers.video_worker import start_worker

def signal_handler(signum, frame):
    """Handler para sinais de interrupção"""
    logger = get_logger("worker.shutdown")
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

def main():
    """Função principal para iniciar workers"""
    parser = argparse.ArgumentParser(description='Start video processing workers')
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=1,
        help='Number of workers to start (default: 1)'
    )
    parser.add_argument(
        '--queue-name', '-q',
        type=str,
        default='video_generation',
        help='Name of the queue to process (default: video_generation)'
    )
    parser.add_argument(
        '--log-level', '-l',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Log level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    logger = get_logger("worker.startup")
    logger.setLevel(getattr(logger, args.log_level.upper()))
    
    # Configurar handlers de sinal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info(f"Starting {args.workers} worker(s) for queue '{args.queue_name}'")
    
    # Verificar se Redis está disponível
    if not queue_manager.use_redis:
        logger.error("Redis is not available. Workers cannot be started.")
        logger.error("Please ensure Redis is running and REDIS_URL is configured.")
        sys.exit(1)
    
    try:
        # Testar conexão com Redis
        queue_manager.redis_client.ping()
        logger.info("Redis connection successful")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        sys.exit(1)
    
    # Iniciar workers
    if args.workers == 1:
        logger.info("Starting single worker...")
        start_worker()
    else:
        logger.info(f"Starting {args.workers} workers...")
        
        import multiprocessing
        processes: List[multiprocessing.Process] = []
        
        try:
            for i in range(args.workers):
                process = multiprocessing.Process(
                    target=start_worker,
                    name=f"VideoWorker-{i+1}"
                )
                process.start()
                processes.append(process)
                logger.info(f"Started worker {i+1} (PID: {process.pid})")
            
            # Aguardar todos os processos
            for process in processes:
                process.join()
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping workers...")
            
            for process in processes:
                if process.is_alive():
                    logger.info(f"Terminating worker {process.name} (PID: {process.pid})")
                    process.terminate()
                    process.join(timeout=5)
                    
                    if process.is_alive():
                        logger.warning(f"Force killing worker {process.name} (PID: {process.pid})")
                        process.kill()
                        process.join()
            
            logger.info("All workers stopped")

if __name__ == "__main__":
    main()