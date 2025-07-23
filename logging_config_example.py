#!/usr/bin/env python3
"""
Example configuration for the AI Video GPT logging system
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.logger import setup_logging, get_logger

def configure_for_development():
    """Configure logging for development environment"""
    setup_logging(
        log_dir="logs",
        environment="development",
        log_level="DEBUG",
        console_output=True,
        max_file_size=5 * 1024 * 1024,  # 5MB
        backup_count=3
    )
    
    logger = get_logger("config.dev")
    logger.info("Logging configured for development")

def configure_for_production():
    """Configure logging for production environment"""
    setup_logging(
        log_dir="/var/log/ai-video-gpt",
        environment="production", 
        log_level="INFO",
        console_output=False,
        max_file_size=50 * 1024 * 1024,  # 50MB
        backup_count=10
    )
    
    logger = get_logger("config.prod")
    logger.info("Logging configured for production")

def configure_for_testing():
    """Configure logging for testing environment"""
    setup_logging(
        log_dir="test-logs",
        environment="development",
        log_level="DEBUG",
        console_output=True
    )
    
    logger = get_logger("config.test")
    logger.info("Logging configured for testing")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Configure AI Video GPT logging")
    parser.add_argument("--env", choices=["development", "production", "testing"], 
                       default="development", help="Environment to configure for")
    
    args = parser.parse_args()
    
    if args.env == "development":
        configure_for_development()
    elif args.env == "production":
        configure_for_production()
    elif args.env == "testing":
        configure_for_testing()
    
    logger = get_logger("config.main")
    logger.info(f"Logging system ready for {args.env} environment")
    print(f"✅ Logging configured for {args.env} environment")