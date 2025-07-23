#!/usr/bin/env python3
"""
Sistema de cache Redis para melhorar performance
"""

import json
import logging
import os
from typing import Any, Optional, Union
from datetime import timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

class CacheManager:
    """Gerenciador de cache com suporte a Redis e fallback em memória"""
    
    def __init__(self):
        self.use_redis = False
        self.redis_client = None
        self.memory_cache = {}
        
        # Tentar conectar ao Redis
        if REDIS_AVAILABLE and os.getenv('USE_REDIS', 'true').lower() == 'true':
            try:
                redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Testar conexão
                self.redis_client.ping()
                self.use_redis = True
                logger.info("Cache Redis conectado com sucesso")
            except Exception as e:
                logger.warning(f"Falha ao conectar Redis, usando cache em memória: {e}")
                self.use_redis = False
        else:
            logger.info("Cache em memória ativado")
    
    def _serialize_value(self, value: Any) -> str:
        """Serializa valor para armazenamento"""
        if isinstance(value, (str, int, float, bool)):
            return json.dumps(value)
        return json.dumps(value, default=str)
    
    def _deserialize_value(self, value: str) -> Any:
        """Deserializa valor do armazenamento"""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera valor do cache"""
        try:
            if self.use_redis:
                value = self.redis_client.get(key)
                if value is not None:
                    return self._deserialize_value(value)
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"Erro ao recuperar cache para chave {key}: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[Union[int, timedelta]] = None) -> bool:
        """Armazena valor no cache"""
        try:
            if self.use_redis:
                serialized_value = self._serialize_value(value)
                if ttl:
                    if isinstance(ttl, timedelta):
                        ttl = int(ttl.total_seconds())
                    return self.redis_client.setex(key, ttl, serialized_value)
                else:
                    return self.redis_client.set(key, serialized_value)
            else:
                self.memory_cache[key] = value
                # Para cache em memória, TTL não é implementado por simplicidade
                return True
        except Exception as e:
            logger.error(f"Erro ao armazenar cache para chave {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        try:
            if self.use_redis:
                return bool(self.redis_client.delete(key))
            else:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    return True
                return False
        except Exception as e:
            logger.error(f"Erro ao deletar cache para chave {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Verifica se chave existe no cache"""
        try:
            if self.use_redis:
                return bool(self.redis_client.exists(key))
            else:
                return key in self.memory_cache
        except Exception as e:
            logger.error(f"Erro ao verificar existência da chave {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Limpa todo o cache"""
        try:
            if self.use_redis:
                return bool(self.redis_client.flushdb())
            else:
                self.memory_cache.clear()
                return True
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do cache"""
        try:
            if self.use_redis:
                info = self.redis_client.info()
                return {
                    'type': 'redis',
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory': info.get('used_memory_human', '0B'),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0)
                }
            else:
                return {
                    'type': 'memory',
                    'keys_count': len(self.memory_cache),
                    'memory_usage': 'N/A'
                }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do cache: {e}")
            return {'type': 'unknown', 'error': str(e)}
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Incrementa valor numérico no cache"""
        try:
            if self.use_redis:
                return self.redis_client.incr(key, amount)
            else:
                current = self.memory_cache.get(key, 0)
                new_value = current + amount
                self.memory_cache[key] = new_value
                return new_value
        except Exception as e:
            logger.error(f"Erro ao incrementar cache para chave {key}: {e}")
            return None
    
    def get_or_set(self, key: str, callback, ttl: Optional[Union[int, timedelta]] = None) -> Any:
        """Recupera valor do cache ou executa callback e armazena resultado"""
        value = self.get(key)
        if value is not None:
            return value
        
        # Executar callback e armazenar resultado
        try:
            result = callback()
            self.set(key, result, ttl)
            return result
        except Exception as e:
            logger.error(f"Erro ao executar callback para chave {key}: {e}")
            return None


# Instância global do cache
cache_manager = CacheManager()


def cache_result(key_prefix: str, ttl: Optional[Union[int, timedelta]] = None):
    """Decorador para cache de resultados de função"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Gerar chave única baseada nos argumentos
            import hashlib
            args_str = str(args) + str(sorted(kwargs.items()))
            args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
            cache_key = f"{key_prefix}:{func.__name__}:{args_hash}"
            
            # Tentar recuperar do cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit para {cache_key}")
                return cached_result
            
            # Executar função e armazenar resultado
            logger.debug(f"Cache miss para {cache_key}")
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator


class ImagePresetsCache:
    """Cache específico para presets de imagem"""
    
    CACHE_KEY = "image_presets"
    TTL = timedelta(hours=24)  # Cache por 24 horas
    
    @staticmethod
    def get_presets() -> Optional[dict]:
        """Recupera presets do cache"""
        return cache_manager.get(ImagePresetsCache.CACHE_KEY)
    
    @staticmethod
    def set_presets(presets: dict) -> bool:
        """Armazena presets no cache"""
        return cache_manager.set(ImagePresetsCache.CACHE_KEY, presets, ImagePresetsCache.TTL)
    
    @staticmethod
    def clear_presets() -> bool:
        """Limpa cache de presets"""
        return cache_manager.delete(ImagePresetsCache.CACHE_KEY)


class APIResponseCache:
    """Cache específico para respostas de API"""
    
    @staticmethod
    def get_api_response(endpoint: str, params_hash: str) -> Optional[dict]:
        """Recupera resposta de API do cache"""
        cache_key = f"api_response:{endpoint}:{params_hash}"
        return cache_manager.get(cache_key)
    
    @staticmethod
    def set_api_response(endpoint: str, params_hash: str, response: dict, ttl: timedelta = timedelta(hours=1)) -> bool:
        """Armazena resposta de API no cache"""
        cache_key = f"api_response:{endpoint}:{params_hash}"
        return cache_manager.set(cache_key, response, ttl)
    
    @staticmethod
    def clear_api_cache(endpoint: str = None) -> bool:
        """Limpa cache de API (específico ou geral)"""
        if endpoint:
            # Limpar cache específico do endpoint (implementação simplificada)
            cache_key = f"api_response:{endpoint}:*"
            return cache_manager.delete(cache_key)
        else:
            # Limpar todo o cache (implementação simplificada)
            return cache_manager.clear()


class JobStatusCache:
    """Cache específico para status de jobs"""
    
    @staticmethod
    def get_job_status(job_id: str) -> Optional[dict]:
        """Recupera status do job do cache"""
        cache_key = f"job_status:{job_id}"
        return cache_manager.get(cache_key)
    
    @staticmethod
    def set_job_status(job_id: str, status: dict, ttl: timedelta = timedelta(minutes=30)) -> bool:
        """Armazena status do job no cache"""
        cache_key = f"job_status:{job_id}"
        return cache_manager.set(cache_key, status, ttl)
    
    @staticmethod
    def clear_job_status(job_id: str) -> bool:
        """Limpa cache de status do job"""
        cache_key = f"job_status:{job_id}"
        return cache_manager.delete(cache_key)