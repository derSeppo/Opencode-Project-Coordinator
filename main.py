#!/usr/bin/env python3
"""
OpenCode AI Coordinator - Main entry point

A production-ready webapp that coordinates AI providers for code generation,
validation, formatting, and other code-related tasks.

Usage:
    python main.py [--host 0.0.0.0] [--port 8000] [--debug]
"""

import argparse
import logging
import sys
from pathlib import Path

from open_coordinator.config.settings import get_settings, Settings
from open_coordinator.api.main import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("open_coordinator.log")
    ]
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="OpenCode AI Coordinator - A production-ready webapp for AI-powered code tasks"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=None,
        help="Server host (default: from settings)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Server port (default: from settings)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of worker processes (default: from settings)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file (default: .env)"
    )
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()
    
    # Load settings
    settings = get_settings()
    
    # Override settings from command line
    if args.host:
        settings.server.host = args.host
    if args.port:
        settings.server.port = args.port
    if args.workers:
        settings.server.workers = args.workers
    if args.debug:
        settings.server.debug = True
    if args.reload:
        settings.server.reload = True
    
    # Configure logging level
    if args.debug or settings.server.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Debug mode enabled")
    else:
        logging.getLogger().setLevel(logging.INFO)
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Server: {settings.server.host}:{settings.server.port}")
    
    # Run the server
    try:
        import uvicorn
        
        uvicorn.run(
            "open_coordinator.api.main:app",
            host=settings.server.host,
            port=settings.server.port,
            reload=settings.server.reload,
            workers=settings.server.workers if settings.server.workers > 1 else None,
            log_level="debug" if args.debug else "info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
