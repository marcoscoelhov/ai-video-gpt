import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from src.utils.cache import (
    CacheManager, 
    ImagePresetsCache, 
    APIResponseCache, 
    JobStatusCache,
    cache_result
)


class TestCacheManager:
    """Test cases for CacheManager class."""
    
    def test_init_with_redis(self, mock_redis):
        """Test CacheManager initialization with Redis."""
        cache = CacheManager(redis_url='redis://localhost:6379/0')
        assert cache.use_redis is True
        assert cache.memory_cache == {}
    
    def test_init_without_redis(self):
        """Test CacheManager initialization without Redis."""
        with patch('redis.Redis', side_effect=Exception('Redis not available')):
            cache = CacheManager(redis_url='redis://localhost:6379/0')
            assert cache.use_redis is False
            assert cache.redis_client is None
    
    def test_set_and_get_redis(self, cache_manager, mock_redis):
        """Test set and get operations with Redis."""
        cache_manager.use_redis = True
        cache_manager.redis_client = mock_redis
        
        # Mock Redis operations
        mock_redis.setex.return_value = True
        mock_redis.get.return_value = json.dumps({'test': 'value'}).encode()
        
        # Test set
        result = cache_manager.set('test_key', {'test': 'value'}, ttl=300)
        assert result is True
        mock_redis.setex.assert_called_once_with('test_key', 300, json.dumps({'test': 'value'}))
        
        # Test get
        value = cache_manager.get('test_key')
        assert value == {'test': 'value'}
        mock_redis.get.assert_called_once_with('test_key')
    
    def test_set_and_get_memory(self, cache_manager):
        """Test set and get operations with memory cache."""
        cache_manager.use_redis = False
        
        # Test set
        result = cache_manager.set('test_key', {'test': 'value'}, ttl=300)
        assert result is True
        
        # Test get
        value = cache_manager.get('test_key')
        assert value == {'test': 'value'}
    
    def test_delete_redis(self, cache_manager, mock_redis):
        """Test delete operation with Redis."""
        cache_manager.use_redis = True
        cache_manager.redis_client = mock_redis
        
        mock_redis.delete.return_value = 1
        
        result = cache_manager.delete('test_key')
        assert result is True
        mock_redis.delete.assert_called_once_with('test_key')
    
    def test_delete_memory(self, cache_manager):
        """Test delete operation with memory cache."""
        cache_manager.use_redis = False
        cache_manager.memory_cache['test_key'] = {
            'value': {'test': 'value'},
            'expires_at': time.time() + 300
        }
        
        result = cache_manager.delete('test_key')
        assert result is True
        assert 'test_key' not in cache_manager.memory_cache
    
    def test_exists_redis(self, cache_manager, mock_redis):
        """Test exists operation with Redis."""
        cache_manager.use_redis = True
        cache_manager.redis_client = mock_redis
        
        mock_redis.exists.return_value = 1
        
        result = cache_manager.exists('test_key')
        assert result is True
        mock_redis.exists.assert_called_once_with('test_key')
    
    def test_exists_memory(self, cache_manager):
        """Test exists operation with memory cache."""
        cache_manager.use_redis = False
        cache_manager.memory_cache['test_key'] = {
            'value': {'test': 'value'},
            'expires_at': time.time() + 300
        }
        
        result = cache_manager.exists('test_key')
        assert result is True
    
    def test_clear_redis(self, cache_manager, mock_redis):
        """Test clear operation with Redis."""
        cache_manager.use_redis = True
        cache_manager.redis_client = mock_redis
        
        mock_redis.flushdb.return_value = True
        
        result = cache_manager.clear()
        assert result is True
        mock_redis.flushdb.assert_called_once()
    
    def test_clear_memory(self, cache_manager):
        """Test clear operation with memory cache."""
        cache_manager.use_redis = False
        cache_manager.memory_cache['key1'] = {'value': 'value1', 'expires_at': time.time() + 300}
        cache_manager.memory_cache['key2'] = {'value': 'value2', 'expires_at': time.time() + 300}
        
        result = cache_manager.clear()
        assert result is True
        assert len(cache_manager.memory_cache) == 0
    
    def test_memory_cache_expiration(self, cache_manager):
        """Test memory cache expiration."""
        cache_manager.use_redis = False
        
        # Set expired item
        cache_manager.memory_cache