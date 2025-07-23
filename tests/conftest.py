import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from flask import Flask
from src.utils.cache import CacheManager
from src.utils.monitoring import MetricsCollector
from src.utils.queue_manager import QueueManager


@pytest.fixture
def app():
    """Create a test Flask application."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_redis():
    """Mock Redis connection for testing."""
    with patch('redis.Redis') as mock_redis:
        mock_instance = Mock()
        mock_redis.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def cache_manager(mock_redis):
    """Create a CacheManager instance for testing."""
    return CacheManager(redis_url='redis://localhost:6379/0')


@pytest.fixture
def metrics_collector(cache_manager):
    """Create a MetricsCollector instance for testing."""
    return MetricsCollector(cache_manager=cache_manager)


@pytest.fixture
def queue_manager():
    """Create a QueueManager instance for testing."""
    return QueueManager(use_redis=False)


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        'script': 'Test script for video generation',
        'image_prompts': ['A beautiful sunset', 'A mountain landscape'],
        'voice_provider': 'auto',
        'voice_type': 'narrator',
        'language': 'pt',
        'video_format': 'standard',
        'effects_preset': 'professional',
        'enable_effects': True,
        'image_preset': 'cinematic'
    }


@pytest.fixture
def mock_video_generation():
    """Mock video generation process."""
    with patch('main.main') as mock_main:
        mock_main.return_value = {
            'success': True,
            'video_path': '/tmp/test_video.mp4',
            'duration': 30.5
        }
        yield mock_main


@pytest.fixture
def api_headers():
    """Common API headers for testing."""
    return {
        'Content-Type': 'application/json',
        'X-API-Key': 'test-api-key'
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ['TESTING'] = 'true'
    os.environ['API_KEY'] = 'test-api-key'
    os.environ['REQUIRE_API_KEY'] = 'true'
    os.environ['REDIS_URL'] = 'redis://localhost:6379/1'  # Use test database
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_system_metrics():
    """Mock system metrics for testing."""
    return {
        'cpu_percent': 45.2,
        'memory_percent': 62.8,
        'disk_percent': 78.5,
        'process_count': 156,
        'uptime_seconds': 3600,
        'timestamp': '2025-01-27T10:00:00'
    }


@pytest.fixture
def mock_api_metrics():
    """Mock API metrics for testing."""
    return {
        'total_requests': 1250,
        'successful_requests': 1180,
        'failed_requests': 70,
        'average_response_time': 245.6,
        'requests_per_hour': 125,
        'error_rate': 5.6
    }