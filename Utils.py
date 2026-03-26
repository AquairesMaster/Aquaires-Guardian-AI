 
"""
logging_config.py

Provides a centralized logging configuration for Guardian House AI.
This ensures consistent formatting and log levels across the system.

In production, this can be extended to:
- Write logs to files
- Stream logs to cloud services
- Add structured JSON logging
"""

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure global logging settings.

    Args:
        level (int): Logging level (default: INFO).
    """
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
)
logging.info("Logging initialized.")



"""
id_generator.py

Utility functions for generating unique identifiers.
Used for conversation IDs, prediction IDs, and other internal references.
"""

import uuid


def generate_id() -> str:
    """
    Generate a unique identifier.

    Returns:
        str: UUID4 string.
    """
    return str(uuid.uuid4())



"""
time_utils.py

Provides helper functions for working with timestamps, durations,
and human-readable time formatting.
"""

from datetime import datetime, timezone


def utc_now() -> str:
    """
    Get the current UTC timestamp in ISO format.

    Returns:
        str: ISO8601 timestamp.
    """
    return datetime.now(timezone.utc).isoformat()


def format_timestamp(ts: datetime) -> str:
    """
    Convert a datetime object to a readable string.

    Args:
        ts (datetime): Timestamp.

    Returns:
        str: Human-readable timestamp.
    """
    return ts.strftime("%Y-%m-%d %H:%M:%S UTC")




"""
crypto.py

Provides lightweight cryptographic utilities for hashing and token generation.
This is NOT intended for high-security cryptography, but for:
- Generating stable hashes
- Creating lightweight tokens
- Obfuscating identifiers

For real cryptographic needs, integrate a proper security library.
"""

import hashlib
import secrets


def sha256_hash(text: str) -> str:
    """
    Compute a SHA-256 hash of a string.

    Args:
        text (str): Input text.

    Returns:
        str: Hex digest.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generate_token(length: int = 32) -> str:
    """
    Generate a secure random token.

    Args:
        length (int): Token length in bytes.

    Returns:
        str: Hex token.
    """
    return secrets.token_hex(length)




