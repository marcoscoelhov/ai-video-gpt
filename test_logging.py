#!/usr/bin/env python3
"""
Test script for the structured logging system
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.logger import setup_logging, get_logger, ai_logger, log_api_call, log_performance, log_cost_tracking
import time
import random

def test_basic_logging():
    """Test basic logging functionality"""
    logger = get_logger("test.basic")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

def test_structured_logging():
    """Test structured logging with extra data"""
    logger = get_logger("test.structured")
    
    # Log with extra structured data
    logger.info("Processing user request", extra={
        'extra_data': {
            'user_id': 'user123',
            'action': 'video_generation',
            'theme': 'cyberpunk city'
        }
    })
    
    # Log with performance metrics
    logger.info("Operation completed", extra={
        'performance_metrics': {
            'operation': 'image_generation',
            'duration_seconds': 2.5,
            'success': True,
            'images_generated': 4
        }
    })

def test_correlation_ids():
    """Test correlation ID functionality"""
    logger = get_logger("test.correlation")
    
    # Test with correlation context
    with ai_logger.correlation_context("test-job-123"):
        logger.info("Starting job processing")
        logger.info("Step 1: Parsing input")
        logger.info("Step 2: Generating content")
        logger.info("Step 3: Finalizing output")
        
        # Test nested correlation
        with ai_logger.correlation_context("sub-task-456"):
            logger.info("Processing sub-task")
            logger.error("Sub-task encountered an issue")

@log_performance("test_operation")
def test_performance_decorator():
    """Test performance logging decorator"""
    logger = get_logger("test.performance")
    logger.info("Doing some work...")
    
    # Simulate some work
    time.sleep(random.uniform(0.1, 0.5))
    
    return "Operation completed"

def test_api_logging():
    """Test API call logging"""
    logger = get_logger("test.api")
    
    # Simulate API calls
    log_api_call("gemini", "generate_script", {'theme': 'space exploration'})
    log_api_call("vertex_ai", "generate_image", {'prompt': 'futuristic city'})
    log_api_call("elevenlabs", "text_to_speech", {'text': 'Hello world'})

def test_cost_tracking():
    """Test cost tracking logging"""
    logger = get_logger("test.cost")
    
    # Simulate cost tracking
    log_cost_tracking("gemini", "script_generation", 0.05, {'tokens': 150})
    log_cost_tracking("vertex_ai", "image_generation", 0.02, {'images': 1})
    log_cost_tracking("elevenlabs", "text_to_speech", 0.001, {'characters': 50})

def test_error_handling():
    """Test error logging"""
    logger = get_logger("test.errors")
    
    try:
        # Simulate an error
        result = 10 / 0
    except Exception as e:
        logger.error("Mathematical error occurred", extra={
            'extra_data': {
                'operation': 'division',
                'numerator': 10,
                'denominator': 0,
                'error_type': type(e).__name__
            }
        }, exc_info=True)

def test_file_operations():
    """Test file operation logging"""
    from utils.logger import log_file_operation
    
    log_file_operation("create", "/tmp/test.txt", {'size': 1024})
    log_file_operation("read", "/tmp/input.json", {'format': 'json'})
    log_file_operation("write", "/tmp/output.mp4", {'format': 'video', 'duration': 30})

def main():
    """Run all tests"""
    # Setup logging in development mode
    setup_logging(
        log_dir="logs",
        environment="development",
        log_level="DEBUG",
        console_output=True
    )
    
    main_logger = get_logger("test.main")
    main_logger.info("Starting structured logging system tests")
    
    print("🧪 Running Structured Logging System Tests\n")
    
    # Run tests with correlation ID
    with ai_logger.correlation_context("test-session-" + str(int(time.time()))):
        
        print("1. Testing basic logging...")
        test_basic_logging()
        
        print("2. Testing structured logging...")
        test_structured_logging()
        
        print("3. Testing correlation IDs...")
        test_correlation_ids()
        
        print("4. Testing performance decorator...")
        result = test_performance_decorator()
        main_logger.info(f"Performance test result: {result}")
        
        print("5. Testing API call logging...")
        test_api_logging()
        
        print("6. Testing cost tracking...")
        test_cost_tracking()
        
        print("7. Testing error handling...")
        test_error_handling()
        
        print("8. Testing file operations...")
        test_file_operations()
    
    main_logger.info("All logging tests completed")
    print("\n✅ All tests completed! Check the logs directory for output files.")
    print(f"   - Main log: logs/ai_video_gpt.log")
    print(f"   - Error log: logs/errors.log")

if __name__ == "__main__":
    main()