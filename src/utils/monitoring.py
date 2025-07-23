#!/usr/bin/env python3
"""
Sistema de monitoramento e métricas para o AI Video GPT
"""

import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

from .cache import cache_manager

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    active_processes: int
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class APIMetrics:
    """Métricas de API"""
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    timestamp: datetime
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class MetricsCollector:
    """Coletor de métricas do sistema"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.system_metrics_history = deque(maxlen=max_history)
        self.api_metrics_history = deque(maxlen=max_history)
        self.error_counts = defaultdict(int)
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0,
            'avg_time': 0,
            'errors': 0
        })
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Coleta métricas do sistema"""
        try:
            # Métricas de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Métricas de memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            
            # Métricas de disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)
            
            # Processos ativos
            active_processes = len(psutil.pids())
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_gb=round(memory_used_gb, 2),
                memory_total_gb=round(memory_total_gb, 2),
                disk_percent=disk_percent,
                disk_used_gb=round(disk_used_gb, 2),
                disk_total_gb=round(disk_total_gb, 2),
                active_processes=active_processes
            )
            
            self.system_metrics_history.append(metrics)
            
            # Armazenar no cache
            cache_manager.set('system_metrics_latest', metrics.to_dict(), ttl=300)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {e}")
            return None
    
    def record_api_call(self, endpoint: str, method: str, status_code: int, 
                       response_time_ms: float, user_agent: str = None, 
                       ip_address: str = None) -> None:
        """Registra chamada de API"""
        try:
            metrics = APIMetrics(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time_ms=response_time_ms,
                timestamp=datetime.now(),
                user_agent=user_agent,
                ip_address=ip_address
            )
            
            self.api_metrics_history.append(metrics)
            
            # Atualizar estatísticas do endpoint
            endpoint_key = f"{method} {endpoint}"
            stats = self.endpoint_stats[endpoint_key]
            stats['count'] += 1
            stats['total_time'] += response_time_ms
            stats['avg_time'] = stats['total_time'] / stats['count']
            
            if status_code >= 400:
                stats['errors'] += 1
                self.error_counts[status_code] += 1
            
            # Armazenar estatísticas no cache
            cache_manager.set('api_stats', dict(self.endpoint_stats), ttl=300)
            cache_manager.set('error_counts', dict(self.error_counts), ttl=300)
            
        except Exception as e:
            logger.error(f"Erro ao registrar chamada de API: {e}")
    
    def get_system_health(self) -> dict:
        """Retorna status de saúde do sistema"""
        try:
            latest_metrics = self.collect_system_metrics()
            if not latest_metrics:
                return {'status': 'unknown', 'message': 'Não foi possível coletar métricas'}
            
            # Determinar status baseado nas métricas
            status = 'healthy'
            issues = []
            
            if latest_metrics.cpu_percent > 80:
                status = 'warning'
                issues.append(f'CPU alta: {latest_metrics.cpu_percent}%')
            
            if latest_metrics.memory_percent > 85:
                status = 'warning'
                issues.append(f'Memória alta: {latest_metrics.memory_percent}%')
            
            if latest_metrics.disk_percent > 90:
                status = 'critical'
                issues.append(f'Disco cheio: {latest_metrics.disk_percent}%')
            
            if latest_metrics.cpu_percent > 95 or latest_metrics.memory_percent > 95:
                status = 'critical'
            
            return {
                'status': status,
                'timestamp': latest_metrics.timestamp.isoformat(),
                'metrics': latest_metrics.to_dict(),
                'issues': issues,
                'cache_stats': cache_manager.get_stats()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter saúde do sistema: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def get_api_statistics(self, hours: int = 24) -> dict:
        """Retorna estatísticas de API das últimas N horas"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [
                m for m in self.api_metrics_history 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {'total_requests': 0, 'endpoints': {}}
            
            # Estatísticas gerais
            total_requests = len(recent_metrics)
            avg_response_time = sum(m.response_time_ms for m in recent_metrics) / total_requests
            error_count = sum(1 for m in recent_metrics if m.status_code >= 400)
            error_rate = (error_count / total_requests) * 100 if total_requests > 0 else 0
            
            # Estatísticas por endpoint
            endpoint_stats = {}
            for endpoint_key, stats in self.endpoint_stats.items():
                endpoint_stats[endpoint_key] = {
                    'requests': stats['count'],
                    'avg_response_time': round(stats['avg_time'], 2),
                    'error_count': stats['errors'],
                    'error_rate': round((stats['errors'] / stats['count']) * 100, 2) if stats['count'] > 0 else 0
                }
            
            return {
                'period_hours': hours,
                'total_requests': total_requests,
                'avg_response_time': round(avg_response_time, 2),
                'error_count': error_count,
                'error_rate': round(error_rate, 2),
                'endpoints': endpoint_stats,
                'error_codes': dict(self.error_counts)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de API: {e}")
            return {'error': str(e)}
    
    def get_performance_trends(self, hours: int = 24) -> dict:
        """Retorna tendências de performance das últimas N horas"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_system_metrics = [
                m for m in self.system_metrics_history 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_system_metrics:
                return {'message': 'Dados insuficientes para análise de tendências'}
            
            # Calcular médias e tendências
            cpu_values = [m.cpu_percent for m in recent_system_metrics]
            memory_values = [m.memory_percent for m in recent_system_metrics]
            
            return {
                'period_hours': hours,
                'cpu': {
                    'avg': round(sum(cpu_values) / len(cpu_values), 2),
                    'min': min(cpu_values),
                    'max': max(cpu_values),
                    'current': cpu_values[-1] if cpu_values else 0
                },
                'memory': {
                    'avg': round(sum(memory_values) / len(memory_values), 2),
                    'min': min(memory_values),
                    'max': max(memory_values),
                    'current': memory_values[-1] if memory_values else 0
                },
                'data_points': len(recent_system_metrics)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter tendências de performance: {e}")
            return {'error': str(e)}


# Instância global do coletor de métricas
metrics_collector = MetricsCollector()


def monitor_api_call(func):
    """Decorador para monitorar chamadas de API"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            response_time = (time.time() - start_time) * 1000
            
            # Registrar métricas de sucesso
            metrics_collector.record_api_call(
                endpoint=func.__name__,
                method='FUNCTION',
                status_code=200,
                response_time_ms=response_time
            )
            
            return result
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            # Registrar métricas de erro
            metrics_collector.record_api_call(
                endpoint=func.__name__,
                method='FUNCTION',
                status_code=500,
                response_time_ms=response_time
            )
            
            raise e
    
    return wrapper