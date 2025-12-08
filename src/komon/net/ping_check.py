"""
Ping connectivity check module.

Provides lightweight ping-based network connectivity checks.
"""

import subprocess
import logging

logger = logging.getLogger(__name__)


def check_ping(host, timeout=3):
    """
    Check network connectivity using ping.
    
    Args:
        host (str): Target host (IP address or hostname)
        timeout (int): Timeout in seconds (default: 3)
    
    Returns:
        bool: True if ping succeeds, False otherwise
    
    Examples:
        >>> check_ping("127.0.0.1")
        True
        >>> check_ping("192.168.1.1", timeout=5)
        True
    """
    try:
        logger.debug("Checking ping: host=%s, timeout=%d", host, timeout)
        
        # Execute ping command
        # -c 1: Send 1 packet
        # -W timeout: Wait timeout seconds for response
        result = subprocess.run(
            ['ping', '-c', '1', '-W', str(timeout), host],
            capture_output=True,
            timeout=timeout + 1,  # Add 1 second buffer for subprocess timeout
            text=True
        )
        
        success = result.returncode == 0
        
        if success:
            logger.debug("Ping succeeded: host=%s", host)
        else:
            logger.warning("Ping failed: host=%s, returncode=%d", host, result.returncode)
            logger.debug("Ping stderr: %s", result.stderr.strip())
        
        return success
        
    except subprocess.TimeoutExpired:
        logger.warning("Ping timeout: host=%s, timeout=%d", host, timeout)
        return False
        
    except FileNotFoundError:
        logger.error("Ping command not found (ping is not installed)")
        return False
        
    except Exception as e:
        logger.error("Ping check failed: host=%s, error=%s", host, e, exc_info=True)
        return False
